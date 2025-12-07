# src/main.py
# Autor: Martin Šilar
# Vstupní bod aplikace

import sys
from src.webcrawler.config import load_config
from src.commands.run_crawler import RunCrawlerCommand
from src.commands.show_profiles import ShowProfilesCommand
from src.commands.exit_app import ExitAppCommand
from src.commands.show_config import ShowConfigCommand
from src.commands.set_profile import SetProfileCommand
from src.commands.toggle_save_html import ToggleSaveHtmlCommand
from src.commands.help_command import HelpCommand

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"


def main():
    config_path = "config.ini"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    config = load_config(config_path)

    commands = {
        "1": RunCrawlerCommand(),
        "2": ShowProfilesCommand(config),
        "3": ShowConfigCommand(config),
        "4": SetProfileCommand(config, config_path),
        "5": ToggleSaveHtmlCommand(config, config_path),
        "6": ExitAppCommand(),
        "7": HelpCommand(config),
    }

    while True:
        html_state = f"{GREEN}ON{RESET}" if config.save_html else f"{RED}OFF{RESET}"

        print(f"""
{CYAN}{BOLD}=============== WEBCRAWLER MENU ==============={RESET}
Aktivní profil: {YELLOW}{config.profile}{RESET}
Ukládání HTML: {html_state}
------------------------------------------------
1) {GREEN}Spustit crawler{RESET}
2) Zobrazit dostupné profily
3) Zobrazit aktuální konfiguraci
4) Změnit profil těžby
5) Přepnout ukládání HTML (ON/OFF)
6) Ukončit aplikaci
7) Nápověda
{CYAN}================================================{RESET}
""")

        cmd = input(f"{BOLD}Vyber možnost:{RESET} ").strip()

        if cmd in commands:
            commands[cmd].execute()
        else:
            print(f"{RED}Neplatná volba. Zadejte číslo 1–7.{RESET}")


if __name__ == "__main__":
    main()
