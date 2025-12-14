# src/commands/help_command.py
# Autor: Martin Šilar
# Nápověda k aplikaci

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
        html_state = "ON" if self.config.save_html else "OFF"
        json_state = "ON" if self.config.open_json_after_finish else "OFF"

        print(f"""
{CYAN}{BOLD}============= NÁPOVĚDA ============={RESET}

1) {GREEN}Spustit crawler{RESET}
   Prochází web v rámci jedné domény a těží data.
   Aktivní profil: {YELLOW}{self.config.profile}{RESET}

2) {GREEN}Profily těžby{RESET}
   contacts → e-maily, telefonní čísla
   seo      → title, meta description, nadpisy
   content  → čistý text stránky

3) {GREEN}Konfigurace{RESET}
   Nastavení lze měnit přímo v aplikaci:
   - Start URL + doména
   - Profil těžby
   - Limity (pages / workers)
   - Přepínače chování

4) {GREEN}Přepínače{RESET}
   HTML ukládání: {YELLOW}{html_state}{RESET}
   Otevření JSON po dokončení: {YELLOW}{json_state}{RESET}

----------------------------------------
Tipy:
- Pokud chceš jen data → vypni HTML.
- Změna URL automaticky nastaví doménu.
- Neplatné URL jsou odmítnuty.
""")
