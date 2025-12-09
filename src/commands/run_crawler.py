# src/commands/run_crawler.py
# Autor: Martin Šilar
# Spuštění crawleru přes Command pattern

import os
import threading
from tqdm import tqdm

from ..webcrawler.crawler import WebCrawler
from ..webcrawler.contacts_extractor import ContactsExtractor
from ..webcrawler.seo_extractor import SEOExtractor
from ..webcrawler.content_extractor import ContentExtractor
from ..webcrawler.config import load_config

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


class RunCrawlerCommand:
    def execute(self):
        print(f"\n{CYAN}{BOLD}========== Spouštím crawler =========={RESET}\n")

        config = load_config()
        crawler = WebCrawler(config)

        if config.profile == "contacts":
            extractor = ContactsExtractor()
        elif config.profile == "seo":
            extractor = SEOExtractor()
        elif config.profile == "content":
            extractor = ContentExtractor()
        else:
            print(f"{RED}Neplatný profil v configu.{RESET}\n")
            return

        crawler.set_extractor(extractor)

        progress = tqdm(total=config.max_pages, desc="Průběh")

        def progress_watcher():
            last = 0
            while crawler.page_count < config.max_pages:
                if crawler.page_count != last:
                    progress.update(crawler.page_count - last)
                    last = crawler.page_count
            progress.update(config.max_pages - last)

        watcher = threading.Thread(target=progress_watcher, daemon=True)
        watcher.start()

        crawler.run()
        watcher.join()
        progress.close()

        output_path = crawler.save_results()

        try:
            os.startfile(output_path)
        except Exception:
            pass

        print(f"\n{GREEN}{BOLD}========== HOTOVO =========={RESET}")
        print(f"Výsledný JSON: {CYAN}{output_path}{RESET}")
        input(f"\n{BOLD}Stiskněte Enter pro návrat do menu...{RESET}")
