# src/webcrawler/seo_extractor.py
# Autor: Martin Šilar
# Extraktor SEO dat – title, meta description, headingy

from bs4 import BeautifulSoup
from .base_extractor import BaseExtractor


class SEOExtractor(BaseExtractor):
    def extract(self, url, html):
        soup = BeautifulSoup(html, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        description = ""
        keywords = ""
        h1 = [h.get_text(strip=True) for h in soup.find_all("h1")]

        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc["content"]

        meta_kw = soup.find("meta", attrs={"name": "keywords"})
        if meta_kw and meta_kw.get("content"):
            keywords = meta_kw["content"]

        if not title and not description and not h1:
            return None

        return {
            "url": url,
            "title": title,
            "description": description,
            "keywords": keywords,
            "h1": h1,
        }
