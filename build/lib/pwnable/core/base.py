from pwnable.core.framework import Framework
from pkgutil import get_data


class Pwnable(Framework):
    def __init__(self):
        Framework.__init__(self, 'base')
        self.name = u'pwnable'
        self._prompt_template = '{start}[{mod}] > '
        self._base_prompt = self._prompt_template.format(start=u'',
                                                         mod=self.name)
        self.show_banner()

    def show_banner(self):
        banner = get_data('pwnable', 'banner.txt')
        print(banner)
