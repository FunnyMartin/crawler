import threading
from ..webcrawler.crawler import WebCrawler

class RunCrawlerCommand:
    def __init__(self, config):
        self.config = config

    def execute(self):
        print("\nSpouštím crawler...\n")

        crawler = WebCrawler(self.config)

        t = threading.Thread(target=crawler.run)
        t.start()
        t.join()

        print("\nCrawler dokončil běh.")
        input("ENTER pro návrat do menu...")
