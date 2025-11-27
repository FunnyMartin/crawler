from bs4 import BeautifulSoup
from .base_extractor import BaseExtractor

class ContentExtractor(BaseExtractor):
    def extract(self, url, html):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n", strip=True)

        if not text:
            return None

        return {
            "url": url,
            "text": text[:2000]
        }
