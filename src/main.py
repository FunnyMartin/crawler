# src/main.py
# Autor: Martin Šilar
# Vstupní bod aplikace

import sys
from src.webcrawler.config import load_config
from src.commands.run_crawler import RunCrawlerCommand
from src.commands.show_profiles import ShowProfilesCommand
from src.commands.show_config import ShowConfigCommand
from src.commands.config_menu import ConfigMenuCommand
from src.commands.help_command import HelpCommand
from src.commands.exit_app import ExitAppCommand

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
        "4": ConfigMenuCommand(config, config_path),
        "5": HelpCommand(config),
        "6": ExitAppCommand(),
    }

    while True:
        html_state = f"{GREEN}ON{RESET}" if config.save_html else f"{RED}OFF{RESET}"

        print(f"""
{CYAN}{BOLD}=============== WEBCRAWLER MENU ==============={RESET}
Profil: {YELLOW}{config.profile}{RESET}
HTML: {html_state}
------------------------------------------------
1) Spustit crawler
2) Zobrazit profily
3) Zobrazit konfiguraci
4) Nastavení aplikace
5) Nápověda
6) Ukončit
{CYAN}================================================{RESET}
""")

        cmd = input(f"{BOLD}Vyber možnost:{RESET} ").strip()

        command = commands.get(cmd)
        if command:
            command.execute()
        else:
            print(f"{RED}Neplatná volba. Zadejte číslo 1–6.{RESET}")


if __name__ == "__main__":
    main()
