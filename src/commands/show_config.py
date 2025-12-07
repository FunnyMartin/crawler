# src/commands/show_config.py
# Autor: Martin Šilar
# Zobrazení aktuální konfigurace crawleru

from .base import Command

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


class ShowConfigCommand(Command):
    def __init__(self, config):
        self.config = config

    def execute(self):
        html_state = f"{GREEN}ON{RESET}" if self.config.save_html else f"{RED}OFF{RESET}"

        print(f"""
{CYAN}{BOLD}Aktuální konfigurace:{RESET}
-----------------------------------
Start URL:       {YELLOW}{self.config.start_url}{RESET}
Doména:          {YELLOW}{self.config.allowed_domain}{RESET}
Profil:          {YELLOW}{self.config.profile}{RESET}
Ukládání HTML:   {html_state}
Max workers:     {self.config.max_workers}
Max pages:       {self.config.max_pages}
-----------------------------------
""")
