from cmd import Cmd
from subprocess import Popen, PIPE


class Framework(Cmd):
    prompt = u'>>>'

    native_color = u'\033[m'
    red_color = u'\033[31m'
    green_color = u'\033[32m'
    orange_color = u'\033[33m'
    blue_color = u'\033[34m'

    def __init__(self, module_name):
        Cmd.__init__(self)
        self._module_name = module_name

    def output(self, line):
        u'''Formats and presents output information.'''
        print('{start_color}[*]{end_color} {line}'.format(
            start_color=self.blue_color, end_color=self.native_color,
            line=line))

    def default(self, param):
        self.do_shell(param)

    def do_exit(self, param):
        u'''Exits the framework.'''
        self._exit = 1
        return True

    def do_back(self, param):
        u'''Alias command for exit.'''
        self.do_exit(param)

    def do_quit(self, param):
        u'''Alias command for exit.'''
        self.do_exit(param)

    def do_shell(self, param):
        u'''Executes a shell command and retrieves the output.

        Arguments:
            param: list
        '''
        self.output(u'Command: {cmd}'.format(cmd=param))
        proc = Popen(param, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()

        if stdout:
            print(u'{start_color}{output}{end_color}'.format(
                start_color=self.orange_color, output=stdout,
                end_color=self.native_color))

        if stdout:
            print(u'{start_color}{output}{end_color}'.format(
                start_color=self.orange_color, output=stderr,
                end_color=self.native_color))
