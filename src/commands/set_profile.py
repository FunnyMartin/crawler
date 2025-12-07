# src/commands/set_profile.py
# Autor: Martin Šilar
# Nastavení profilu těžby a uložení do config.ini

import configparser
from .base import Command

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


class SetProfileCommand(Command):
    def __init__(self, config, config_path="config.ini"):
        self.config = config
        self.config_path = config_path

    def execute(self):
        print(f"{CYAN}Dostupné profily:{RESET}")
        print("1) contacts")
        print("2) seo")
        print("3) content")
        print("4) custom")

        choice = input("\nZadej volbu: ")

        mapping = {
            "1": "contacts",
            "2": "seo",
            "3": "content",
            "4": "custom"
        }

        if choice not in mapping:
            print(f"{RED}Neplatná volba.{RESET}")
            return

        new_profile = mapping[choice]
        self.config.profile = new_profile

        parser = configparser.ConfigParser()
        parser.read(self.config_path, encoding="utf-8")
        parser["crawler"]["profile"] = new_profile

        with open(self.config_path, "w", encoding="utf-8") as f:
            parser.write(f)

        print(f"{GREEN}Profil úspěšně uložen: {new_profile}{RESET}")
