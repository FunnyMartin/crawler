import re
from bs4 import BeautifulSoup


class BaseExtractor:
    """
    Společná logika pro extraktory.
    """

    def __init__(self):
        self.crawler = None

    def set_crawler(self, crawler):
        self.crawler = crawler

    def extract(self, url: str, html: str):
        raise NotImplementedError

    def _strip_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ")
        return re.sub(r"\s+", " ", text).strip()
