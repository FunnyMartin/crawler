# src/commands/show_profiles.py
# Autor: Martin Šilar
# Výpis dostupných profilů těžby

from .base import Command

class ShowProfilesCommand(Command):
    def __init__(self, config):
        self.config = config

    def execute(self):
        print("\nDostupné profily těžby:")
        print(" - contacts  → e-maily, telefonní čísla")
        print(" - seo       → title, meta, nadpisy H1–H3")
        print(" - content   → textový obsah stránky\n")

