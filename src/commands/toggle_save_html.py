# src/commands/toggle_save_html.py
# Autor: Martin Šilar
# Přepínání ukládání HTML stránek v konfiguraci

import configparser
from .base import Command

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


class ToggleSaveHtmlCommand(Command):
    def __init__(self, config, config_path="config.ini"):
        self.config = config
        self.config_path = config_path

    def execute(self):
        new_value = not self.config.save_html
        self.config.save_html = new_value

        parser = configparser.ConfigParser()
        parser.read(self.config_path, encoding="utf-8")
        parser["crawler"]["save_html"] = str(new_value).lower()

        with open(self.config_path, "w", encoding="utf-8") as f:
            parser.write(f)

        state = f"{GREEN}ON{RESET}" if new_value else f"{RED}OFF{RESET}"

        print(f"\n{CYAN}--------------------------------{RESET}")
        print(f"{BOLD}  Ukládání HTML bylo změněno.{RESET}")
        print(f"  Nový stav: {state}")
        print(f"{CYAN}--------------------------------{RESET}\n")
