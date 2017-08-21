# stdlib
from cmd import Cmd
from pkgutil import get_data
from sys import exit
from sqlite3 import connect

# third-party
from pydispatch import dispatcher

# framework
from pwnable.core.helpers import color

class Pwnable(Cmd):
    def __init__(self, args=None, api=False):
        Cmd.__init__(self)

        # setup
        self.global_options = {}
        self.args = args
        self.conn = self.connect_database()
        dispatcher.connect(self.handle_event, sender=dispatcher.Any)

        # display
        self.prompt = '(PWNable) > '
        self.do_help.__func__.__doc__ = '''Displays the help menu.'''
        self.doc_header = 'Commands'
        self.show_banner()

    # Connection Methods
    def connect_database(self):
        try:
            conn = connect('pwnable.db', check_same_thread=False)
            conn.text_factory = str
            conn.isolation_level = None
            return conn
        except Exception:
            print(color('[!] Could not connect to pwnable database'))
            print(color('[!] Please ensure database is configured'))
            exit(1)

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
        if self.args.debug:
            f = open("empyre.debug", 'a')
            f.write(helpers.get_datetime() + " " + sender + " : " + signal + "\n")
            f.close()

            if self.args.debug == '2':
                # if --debug 2, also print the output to the screen
                print " " + sender + " : " + signal

        # display specific signals from the agents.
        if sender == "Agents":
            if "[+] Initial agent" in signal:
                print helpers.color(signal)

            elif "[!] Agent" in signal and "exiting" in signal:
                print helpers.color(signal)

            elif "WARNING" in signal or "attempted overwrite" in signal:
                print helpers.color(signal)

            elif "on the blacklist" in signal:
                print helpers.color(signal)

        elif sender == "EmPyreServer":
            if "[!] Error starting listener" in signal:
                print helpers.color(signal)

        elif sender == "Listeners":
            print helpers.color(signal)

    # Show Methods
    def show_banner(self):
        banner = get_data('pwnable', 'banner.txt')
        print(banner)
