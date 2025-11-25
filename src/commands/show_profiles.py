from .base import Command

class ShowProfilesCommand(Command):
    def __init__(self, config):
        self.config = config

    def execute(self):
        print("\nDostupné profily těžby dat:")
        for p in self.config.profiles:
            print(f" - {p}")
        print()
