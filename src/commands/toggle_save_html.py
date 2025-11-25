import configparser
from .base import Command

class ToggleSaveHtmlCommand(Command):
    def __init__(self, config, config_path="config.ini"):
        self.config = config
        self.config_path = config_path

    def execute(self):
        new_value = not self.config.save_html
        self.config.save_html = new_value

        parser = configparser.ConfigParser()
        parser.read(self.config_path, encoding="utf-8")
        parser["crawler"]["save_html"] = str(new_value).lower()

        with open(self.config_path, "w", encoding="utf-8") as f:
            parser.write(f)

        print(f"Ukládání HTML je nyní: {'ON' if new_value else 'OFF'}")
