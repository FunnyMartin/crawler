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
        html_state = "ON" if self.config.save_html else "OFF"
        open_state = "ON" if self.config.open_json_after_finish else "OFF"

        print(f"""
{CYAN}{BOLD}============= NÁPOVĚDA ============={RESET}

1) {GREEN}Spustit crawler{RESET}
   Spustí vícevláknové procházení webu v rámci jedné domény.
   Podle aktivního profilu extrahuje data a uloží je do JSON.
   Profil: {YELLOW}{self.config.profile}{RESET}

2) {GREEN}Zobrazit profily{RESET}
   Vypíše všechny podporované režimy těžby dat
   (contacts / seo / content).

3) {GREEN}Zobrazit konfiguraci{RESET}
   Zobrazí aktuální nastavení aplikace:
   URL, doménu, limity, profil a přepínače.

4) {GREEN}Nastavení aplikace{RESET}
   Otevře konfigurační menu, kde lze:
   - změnit profil těžby
   - zapnout/vypnout ukládání HTML (aktuálně: {YELLOW}{html_state}{RESET})
   - zapnout/vypnout otevření JSON po dokončení (aktuálně: {YELLOW}{open_state}{RESET})
   - změnit max_pages a max_workers
   Všechny změny se ukládají přímo do config.ini.

5) {GREEN}Nápověda{RESET}
   Zobrazí tento přehled příkazů.

6) {GREEN}Ukončit aplikaci{RESET}
   Okamžitě a bezpečně ukončí program.

----------------------------------------
Tip:
- Pokud ti jde jen o data → vypni ukládání HTML.
- Nastavení se projeví při dalším spuštění crawleru.
""")
