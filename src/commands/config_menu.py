# src/commands/config_menu.py
# Autor: Martin Šilar
# Centrální menu pro úpravu konfigurace aplikace

import configparser
from .base import Command

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"


class ConfigMenuCommand(Command):
    def __init__(self, config, config_path="config.ini"):
        self.config = config
        self.config_path = config_path

    def _save(self, key, value):
        parser = configparser.ConfigParser()
        parser.read(self.config_path, encoding="utf-8")
        parser["crawler"][key] = str(value).lower() if isinstance(value, bool) else str(value)
        with open(self.config_path, "w", encoding="utf-8") as f:
            parser.write(f)

    def execute(self):
        while True:
            print(f"""
{CYAN}{BOLD}=========== NASTAVENÍ APLIKACE ==========={RESET}
Aktivní profil: {YELLOW}{self.config.profile}{RESET}
Ukládání HTML: {'ON' if self.config.save_html else 'OFF'}
Otevřít JSON po dokončení: {'ON' if self.config.open_json_after_finish else 'OFF'}
-------------------------------------------------
1) Změnit profil těžby
2) Přepnout ukládání HTML
3) Přepnout otevření JSON po dokončení
4) Změnit max_pages
5) Změnit max_workers
6) Zpět
{CYAN}=========================================={RESET}
""")

            choice = input(f"{BOLD}Vyber volbu:{RESET} ").strip()

            if choice == "1":
                self._set_profile()
            elif choice == "2":
                self._toggle_save_html()
            elif choice == "3":
                self._toggle_open_json()
            elif choice == "4":
                self._set_max_pages()
            elif choice == "5":
                self._set_max_workers()
            elif choice == "6":
                return
            else:
                print(f"{RED}Neplatná volba.{RESET}")

    def _set_profile(self):
        print("\nDostupné profily:")
        for i, p in enumerate(self.config.profiles, start=1):
            print(f"{i}) {p}")

        choice = input("Vyber profil: ").strip()
        try:
            new_profile = self.config.profiles[int(choice) - 1]
        except (IndexError, ValueError):
            print(f"{RED}Neplatná volba.{RESET}")
            return

        self.config.profile = new_profile
        self._save("profile", new_profile)
        print(f"{GREEN}Profil nastaven na: {new_profile}{RESET}")

    def _toggle_save_html(self):
        self.config.save_html = not self.config.save_html
        self._save("save_html", self.config.save_html)
        state = "ON" if self.config.save_html else "OFF"
        print(f"{GREEN}Ukládání HTML: {state}{RESET}")

    def _toggle_open_json(self):
        self.config.open_json_after_finish = not self.config.open_json_after_finish
        self._save("open_json_after_finish", self.config.open_json_after_finish)
        state = "ON" if self.config.open_json_after_finish else "OFF"
        print(f"{GREEN}Otevírání JSON po dokončení: {state}{RESET}")

    def _set_max_pages(self):
        value = input("Zadej max_pages: ").strip()
        if not value.isdigit():
            print(f"{RED}Musí být číslo.{RESET}")
            return

        self.config.max_pages = int(value)
        self._save("max_pages", value)
        print(f"{GREEN}max_pages nastaveno na {value}{RESET}")

    def _set_max_workers(self):
        value = input("Zadej max_workers: ").strip()
        if not value.isdigit():
            print(f"{RED}Musí být číslo.{RESET}")
            return

        self.config.max_workers = int(value)
        self._save("max_workers", value)
        print(f"{GREEN}max_workers nastaveno na {value}{RESET}")

