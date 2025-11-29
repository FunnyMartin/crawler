# src/commands/run_crawler.py
# Autor: Martin Šilar
# Spuštění crawleru přes Command pattern

import threading
from tqdm import tqdm

from ..webcrawler.crawler import WebCrawler
from ..webcrawler.contacts_extractor import ContactsExtractor
from ..webcrawler.seo_extractor import SEOExtractor
from ..webcrawler.content_extractor import ContentExtractor
from ..webcrawler.config import load_config


class RunCrawlerCommand:
    def execute(self):
        print("\n--- Spouštím crawler ---\n")

        config = load_config()
        crawler = WebCrawler(config)

        if config.profile == "contacts":
            extractor = ContactsExtractor()
        elif config.profile == "seo":
            extractor = SEOExtractor()
        elif config.profile == "content":
            extractor = ContentExtractor()
        else:
            print("Neplatný profil v configu.")
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
        print(f"\nTěžba dokončena. Data uložena do: {output_path}")
