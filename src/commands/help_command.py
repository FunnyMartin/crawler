# src/commands/help_command.py
# Autor: Martin Šilar
# Nápověda k jednotlivým příkazům

from .base import Command

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"


class HelpCommand(Command):
    def __init__(self, config):
        self.config = config

    def execute(self):
        html_state = f"ON" if self.config.save_html else "OFF"

        print(f"""
{CYAN}{BOLD}============= NÁPOVĚDA ============={RESET}

1) {GREEN}Spustit crawler{RESET}
   Spustí vícevláknové procházení webu.
   Extrahuje data podle profilu a uloží JSON.

2) {GREEN}Zobrazit profily{RESET}
   Vypíše možné režimy těžby dat.

3) {GREEN}Zobrazit konfiguraci{RESET}
   Zobrazí aktuální parametry aplikace.

4) {GREEN}Změnit profil těžby{RESET}
   Přepne mezi: contacts / seo / content / custom.

5) {GREEN}Toggle ukládání HTML{RESET}
   Přepíná ukládání stažených HTML (aktuálně: {YELLOW}{html_state}{RESET}).

6) {GREEN}Ukončit aplikaci{RESET}
   Bezpečně ukončí program.

----------------------------------------
Tip: Pokud chceš jen data → vypni HTML.
""")
