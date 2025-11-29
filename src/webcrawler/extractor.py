# src/webcrawler/extractor.py
# Autor: Martin Šilar
# Původní extraktor – nahrazen specializovanými extraktory

from .contacts_extractor import ContactsExtractor
from .seo_extractor import SEOExtractor
from .content_extractor import ContentExtractor


def build_extractor(profile_name: str):
    name = profile_name.lower()

    if name == "contacts":
        return ContactsExtractor()

    if name == "seo":
        return SEOExtractor()

    if name == "content":
        return ContentExtractor()

    raise ValueError(f"Unknown profile: {profile_name}")
