# src/commands/show_profiles.py
# Autor: Martin Šilar
# Výpis dostupných profilů těžby

from .base import Command


class ShowProfilesCommand(Command):
    def __init__(self, config):
        self.config = config

    def execute(self):
        print("\nDostupné profily těžby dat:")
        for p in self.config.profiles:
            print(f" - {p}")
        print()
