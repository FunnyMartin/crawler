# src/main.py
# Autor: Martin Šilar

import sys
import time
from src.webcrawler.config import load_config
from src.commands.run_crawler import RunCrawlerCommand
from src.commands.show_profiles import ShowProfilesCommand
from src.commands.exit_app import ExitAppCommand
from commands.show_config import ShowConfigCommand
from commands.set_profile import SetProfileCommand
from commands.toggle_save_html import ToggleSaveHtmlCommand
from src.webcrawler.crawler import WebCrawler


def run_with_ui(crawler: WebCrawler):
    crawler.start_async()

    while crawler.is_running():
        done = crawler.page_count
        total = crawler.config.max_pages
        percent = (done / total) * 100 if total > 0 else 0

        bar_len = 40
        filled = int(bar_len * done / total) if total > 0 else 0
        bar = "[" + "#" * filled + "-" * (bar_len - filled) + "]"

        with crawler.ui_lock:
            status = crawler.ui_status

        print(f"\r{bar} {percent:5.1f}% | {status:60}", end="", flush=True)
        time.sleep(0.1)

    crawler.wait()
    print("\nCrawling dokončen.\n")


class RunCrawlerCommand:
    def __init__(self, config):
        self.config = config

    def execute(self):
        crawler = WebCrawler(self.config)
        run_with_ui(crawler)


def main():
    required_packages = [
        "requests",
        "bs4"
    ]

    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            print(f"Chybí balíček: {pkg}.")
            print("Spusť: pip install -r requirements.txt")
            input("Stiskni ENTER pro ukončení...")
            sys.exit(1)

    config_path = "config.ini"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    config = load_config(config_path)

    commands = {
        "1": RunCrawlerCommand(config),
        "2": ShowProfilesCommand(config),
        "3": ShowConfigCommand(config),
        "4": SetProfileCommand(config, config_path),
        "5": ToggleSaveHtmlCommand(config, config_path),
        "6": ExitAppCommand()
    }

    while True:
        print("------------- MENU -------------")
        print("1) Spustit crawler")
        print("2) Zobrazit dostupné profily")
        print("3) Zobrazit aktuální konfiguraci")
        print("4) Změnit profil těžby")
        print("5) Zapnout/vypnout ukládání HTML")
        print("6) Ukončit")
        print("--------------------------------")

        cmd = input("Zadej volbu: ").strip()
        if cmd in commands:
            commands[cmd].execute()
        else:
            print("Neplatná volba.")


if __name__ == "__main__":
    main()
