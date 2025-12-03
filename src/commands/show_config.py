# src/commands/show_config.py
# Autor: Martin Šilar
# Zobrazení aktuální konfigurace crawleru

from .base import Command


class ShowConfigCommand(Command):
    def __init__(self, config):
        self.config = config

    def execute(self):
        html_state = "ON" if self.config.save_html else "OFF"

        print("\nAktuální konfigurace:")
        print("---------------------------")
        print(f"Start URL:      {self.config.start_url}")
        print(f"Doména:         {self.config.allowed_domain}")
        print(f"Profil:         {self.config.profile}")
        print(f"Ukládání HTML:  {html_state}")
        print(f"Max workers:    {self.config.max_workers}")
        print(f"Max pages:      {self.config.max_pages}")
        print("---------------------------\n")
