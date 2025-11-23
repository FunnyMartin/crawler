# src/main.py
# Autor: Martin Šilar
# Vstupní skript – spouští WebCrawler

import sys
from webcrawler.config import load_config
from webcrawler.crawler import WebCrawler


def main():
    config_path = "config.ini"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    config = load_config(config_path)
    crawler = WebCrawler(config)
    crawler.run()


if __name__ == "__main__":
    main()
