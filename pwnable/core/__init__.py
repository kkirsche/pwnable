from pwnable.core.pwnable import Pwnable


def cli():
    try:
        cli = Pwnable()
        cli.cmdloop()
    except KeyboardInterrupt:
        pass
