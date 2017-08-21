# stdlib
from cmd import Cmd
from pkgutil import get_data
from pkg_resources import get_distribution
from sys import exit
from sqlite3 import connect
from os import geteuid
from os.path import isfile
from subprocess import Popen, PIPE
from tempfile import TemporaryFile

# third-party
from pydispatch import dispatcher

# framework
from helpers import color, get_config


# custom exceptions used for nested menu navigation
class NavMain(Exception):
    pass


class NavScanning(Exception):
    pass


class Pwnable(Cmd):

    def __init__(self, args=None, api=False):
        Cmd.__init__(self)

        # setup
        self.global_options = {}
        self.conn = self.connect_database()
        self.args = args
        self.is_root = get_config(self.conn, 'root_user')
        dispatcher.connect(self.handle_event, sender=dispatcher.Any)

        # state
        self.menu_state = 'Main'

        # display
        self.prompt = '(PWNable) > '
        self.do_help.__func__.__doc__ = '''Displays the help menu.'''
        self.doc_header = 'Commands'

        if not api:
            self.start()

    # Database Methods
    def connect_database(self):
        db_name = 'pwnable.db'
        exists = self.check_for_db(db_name=db_name)
        try:
            conn = connect(db_name, check_same_thread=False)
            conn.text_factory = str
            conn.isolation_level = None
            if not exists:
                self.setup_db(conn=conn)
            return conn
        except Exception:
            print(color('[!] Could not connect to pwnable database'))
            print(color('[!] Please ensure database is configured'))
            exit(1)

    def check_for_db(self, db_name):
        if not isfile(db_name):
            return False
        return True

    def setup_db(self, conn):
        default_port = 8080
        api_server_version = 'ngninx/1.13.3'
        conn.execute('DROP TABLE IF EXISTS config')
        conn.execute('''CREATE TABLE config (
          "root_user" boolean,
          "default_port" text,
          "server_version" text
        )''')
        conn.execute('INSERT INTO config VALUES (?,?,?)', (False, default_port,
                                                           api_server_version))
        conn.commit()
        print('\n [*] Database setup completed!\n')

    # Event Methods
    def handle_event(self, signal, sender):
        """
        Default event handler.
        Signal Senders:
            EmPyre          -   the main EmPyre controller (this file)
            Agents          -   the Agents handler
            Listeners       -   the Listeners handler
            HttpHandler     -   the HTTP handler
            EmPyreServer    -   the EmPyre HTTP server
        """

        # if --debug X is passed, log out all dispatcher signals
        if self.args:
            if self.args.debug:
                print('Debugging!')

    # Show Methods
    def show_banner(self):
        banner_tmpl = get_data('pwnable', 'banner.txt')
        print(banner_tmpl.format(version=get_distribution('pwnable').version))

    # print a nicely formatted help menu
    # stolen/adapted from recon-ng
    def print_topics(self, header, cmds, cmdlen, maxcol):
        if cmds:
            self.stdout.write("%s\n" % str(header))
            if self.ruler:
                self.stdout.write("%s\n" % str(self.ruler * len(header)))
            for c in cmds:
                self.stdout.write(
                    "%s %s\n" % (c.ljust(17), getattr(self, 'do_' + c).__doc__))
            self.stdout.write("\n")

    # State Methods
    def check_root(self):
        '''Check if PWNable has been run as root, and alert the user.'''
        try:
            if geteuid() != 0:
                if self.is_root:
                    self.show_banner()
                    print(
                        '[!] Warning: Running PWNable as non-root will likely fail to run certain modules!'
                    )
                    while True:
                        confirm = raw_input(
                            color(
                                '[>] Are you sure you want to continue? [y/n]: '
                            ))
                        if confirm.lower().startswith('y'):
                            return
                        elif confirm.lower().startswith('n'):
                            self.shutdown()
                            exit(0)
                else:
                    pass
            else:
                if self.is_root:
                    pass
                else:
                    cur = self.conn.cursor()
                    cur.execute('UPDATE config SET rootuser = 1')
                    cur.close()
        except Exception as e:
            print(repr(e))

    # Main Methods
    def start(self):
        dispatcher.send('[*] PWNable is starting up...', sender='PWNable')

    def shutdown(self):
        print('\n{message}'.format(message=color('[!] Shutting down...\n')))
        dispatcher.send('[*] PWNable shutting down...', sender='PWNable')
        if self.conn:
            self.conn.close()

    def cmdloop(self):
        self.check_root()
        while True:
            try:
                if self.menu_state == 'Scanning':
                    self.do_scanning('')
                elif self.menu_state == 'Validation':
                    self.do_validation('')
                else:
                    self.show_banner()

                num_modules = []
                if num_modules:
                    num_modules = len(num_modules)
                else:
                    num_modules = 0

                num_modules_output = color(num_modules, 'green')
                line = '{spaces}{num_modules} modules currently loaded\n'.format(
                    spaces=' ' * 20, num_modules=num_modules_output)
                print(line)
                Cmd.cmdloop(self)
                # handle those pesky ctrl+c's
            except KeyboardInterrupt:
                self.menu_state = "Main"
                try:
                    choice = raw_input(
                        color("\n[>] Exit? [y/N] ", "red"))
                    if choice.lower() != "" and choice.lower()[0] == "y":
                        self.shutdown()
                        return True
                    else:
                        continue
                except KeyboardInterrupt:
                    continue

            # exception used to signal jumping to "Main" menu
            except NavMain:
                self.menu_state = "Main"

            # exception used to signal jumping to "Agents" menu
            except NavScanning:
                self.menu_state = "Scanning"

            except Exception as e:
                print(color("[!] Exception: {e}".format(e=e)))

    def default(self, params):
        pass

    def do_shell(self, params):
        '''Executes shell commands.'''
        with TemporaryFile() as stdoutf:
            with TemporaryFile() as stderrf:
                proc = Popen(
                    params,
                    shell=True,
                    stdout=stdoutf,
                    stderr=stderrf,
                    stdin=PIPE)
                print('[*] Executing Command: {cmd}'.format(cmd=params))
                proc.wait()

                # write to the file so we have results
                stdoutf.flush()
                stderrf.flush()
                stdoutf.seek(0)
                stderrf.seek(0)

                stdout = stdoutf.read()
                stderr = stderrf.read()
                if stdout:
                    print(stdout)
                if stderr:
                    print(stderr)

    def do_scanning(self, line):
        '''Jump to scanning menu'''
        try:
            s = ScanningMenu(self)
            s.cmdloop()
        except Exception as e:
            raise e

    def do_exit(self, param):
        '''Exit PWNable.'''
        raise KeyboardInterrupt


class ScanningMenu(Cmd):
    def __init__(self, mainMenu):
        Cmd.__init__(self)

        self.mainMenu = mainMenu

        self.doc_header = 'Commands'

        # set the prompt text
        self.prompt = '(PWNable: {module}) > '.format(module=color(
            "scanning", color="blue"))

    def do_back(self, line):
        "Return back a menu."
        return NavMain()

    def emptyline(self):
        pass

    # print a nicely formatted help menu
    # stolen/adapted from recon-ng
    def print_topics(self, header, cmds, cmdlen, maxcol):
        if cmds:
            self.stdout.write("%s\n" % str(header))
            if self.ruler:
                self.stdout.write("%s\n" % str(self.ruler * len(header)))
            for c in cmds:
                self.stdout.write(
                    "%s %s\n" % (c.ljust(17), getattr(self, 'do_' + c).__doc__))
            self.stdout.write("\n")

    def do_main(self, line):
        '''Go back to the main menu.'''
        raise NavMain()

    def do_nmap(self, param):
        '''Execute an nmap scan'''
        pass

    def do_exit(self, param):
        '''Exit PWNable.'''
        raise KeyboardInterrupt
