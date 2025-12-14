# src/main.py
# Autor: Martin Šilar
# Vstupní bod aplikace

import sys
from src.webcrawler.config import load_config
from src.commands.run_crawler import RunCrawlerCommand
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
        "2": ShowConfigCommand(config),
        "3": ConfigMenuCommand(config, config_path),
        "4": HelpCommand(config),
        "5": ExitAppCommand(),
    }

    while True:
        html_state = f"{GREEN}ON{RESET}" if config.save_html else f"{RED}OFF{RESET}"
        json_state = f"{GREEN}ON{RESET}" if config.open_json_after_finish else f"{RED}OFF{RESET}"

        print(f"""
{CYAN}{BOLD}=============== WEBCRAWLER MENU ==============={RESET}
Profil: {YELLOW}{config.profile}{RESET}
HTML: {html_state} | JSON auto-open: {json_state}
------------------------------------------------
1) Spustit crawler
2) Zobrazit konfiguraci
3) Nastavení aplikace
4) Nápověda
5) Ukončit
{CYAN}================================================{RESET}
""")

        cmd = input(f"{BOLD}Vyber možnost:{RESET} ").strip()

        command = commands.get(cmd)
        if command:
            command.execute()
        else:
            print(f"{RED}Neplatná volba.{RESET}")


if __name__ == "__main__":
    main()
