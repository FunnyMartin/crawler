from .base import Command

class ExitAppCommand(Command):
    def execute(self):
        print("\nUkončuji aplikaci...\n")
        exit(0)
