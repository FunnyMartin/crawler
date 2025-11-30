# src/webcrawler/seo_extractor.py
# Autor: Martin Šilar
# SEO extractor – získává title, description, keywords a headings

from bs4 import BeautifulSoup
from .base_extractor import BaseExtractor


class SEOExtractor(BaseExtractor):
    def extract(self, url: str, html: str):
        soup = BeautifulSoup(html, "html.parser")

        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else ""

        desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_description = desc_tag.get("content", "").strip() if desc_tag else ""

        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        if keywords_tag and keywords_tag.get("content"):
            meta_keywords = [k.strip() for k in keywords_tag["content"].split(",")]
        else:
            meta_keywords = []

        headings = []
        for h in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            for tag in soup.find_all(h):
                text = tag.get_text(strip=True)
                if text:
                    headings.append(text)

        result = {
            "url": url,
            "title": title,
            "meta_description": meta_description,
            "meta_keywords": meta_keywords,
            "headings": headings,
        }

        if not (title or meta_description):
            return None

        return result
