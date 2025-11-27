import sys
from src.webcrawler.config import load_config
from src.commands.run_crawler import RunCrawlerCommand
from src.commands.show_profiles import ShowProfilesCommand
from src.commands.exit_app import ExitAppCommand
from src.commands.show_config import ShowConfigCommand
from src.commands.set_profile import SetProfileCommand
from src.commands.toggle_save_html import ToggleSaveHtmlCommand


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
