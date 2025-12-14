# src/commands/run_crawler.py
# Autor: Martin Šilar
# Spuštění crawleru přes Command pattern

import os
import threading
import time
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
            print(f"{RED}Neplatný profil v configu.{RESET}")
            return

        crawler.set_extractor(extractor)

        progress = tqdm(
            total=config.max_pages,
            desc="Průběh",
            dynamic_ncols=True
        )

        def progress_watcher():
            last = 0
            while True:
                current = crawler.page_count
                if current != last:
                    progress.update(current - last)
                    last = current

                if not crawler_running[0]:
                    break

                time.sleep(0.1)

        crawler_running = [True]

        watcher = threading.Thread(target=progress_watcher, daemon=True)
        watcher.start()

        crawler.run()

        crawler_running[0] = False
        watcher.join()
        progress.close()

        output_path = crawler.save_results()

        if config.open_json_after_finish:
            try:
                os.startfile(output_path)
            except Exception:
                pass

        print(f"\n{GREEN}{BOLD}========== HOTOVO =========={RESET}")
        print(f"Výsledný JSON: {CYAN}{output_path}{RESET}")
        input(f"\n{BOLD}Stiskněte Enter pro návrat do menu...{RESET}")
