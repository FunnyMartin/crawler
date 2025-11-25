from .base import Command

class ShowConfigCommand(Command):
    def __init__(self, config):
        self.config = config

    def execute(self):
        print("\nAktuální konfigurace:")
        print("----------------------")
        print(f"Start URL:        {self.config.start_url}")
        print(f"Doména:           {self.config.allowed_domain}")
        print(f"Profil těžby:     {self.config.profile}")
        print(f"Ukládání HTML:    {self.config.save_html}")
        print(f"Max workers:      {self.config.max_workers}")
        print(f"Max pages:        {self.config.max_pages}")
        print("----------------------\n")
