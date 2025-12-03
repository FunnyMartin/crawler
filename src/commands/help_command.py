# src/commands/help_command.py
# Autor: Martin Šilar
# Nápověda k jednotlivým příkazům

from .base import Command


class HelpCommand(Command):
    def __init__(self, config):
        self.config = config

    def execute(self):
        html_state = "ON" if self.config.save_html else "OFF"

        print("\n============= NÁPOVĚDA =============")
        print("Toto je přehled všech dostupných příkazů:")
        print("----------------------------------------")
        print("1) Spustit crawler")
        print("   Spustí vícevláknové procházení webu,")
        print("   podle zvoleného profilu extrahuje data,")
        print("   zobrazí progress bar a uloží výsledky do JSON.")
        print()
        print("2) Zobrazit profily")
        print("   Vypíše podporované režimy těžby dat a jejich význam.")
        print()
        print("3) Zobrazit konfiguraci")
        print("   Ukáže aktuální nastavení (URL, doména, profil, HTML ON/OFF).")
        print()
        print("4) Změnit profil těžby")
        print("   Umožňuje přepnout mezi: contacts / seo / content / custom.")
        print()
        print("5) Zapnout/vypnout ukládání HTML")
        print(f"   Přepne ukládání HTML souborů (aktuálně: {html_state}).")
        print()
        print("6) Ukončit aplikaci")
        print("   Bezpečně ukončí program.")
        print("----------------------------------------")
        print("Tip: Spusť crawler s vypnutým HTML, pokud ti jde jen o data.\n")
