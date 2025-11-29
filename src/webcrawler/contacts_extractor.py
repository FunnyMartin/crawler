# src/webcrawler/contacts_extractor.py
# Autor: Martin Šilar
# Extraktor kontaktů – emaily a telefonní čísla

import re
from .base_extractor import BaseExtractor


class ContactsExtractor(BaseExtractor):
    """
    Extrahuje e-maily a česká telefonní čísla.
    Ukládá pouze stránky, kde se objevuje alespoň jeden email nebo telefon.
    """

    EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    PHONE_CANDIDATE_REGEX = r"(?:\+?\d[\d\s\-]{8,15})"

    def extract(self, url: str, html: str):
        if not html:
            return None

        text = self._strip_html(html)

        emails = self._extract_emails(text)
        phones = self._extract_phones(text)

        if not emails and not phones:
            return None

        return {
            "url": url,
            "emails": emails,
            "phones": phones
        }

    def _extract_emails(self, text: str):
        emails = re.findall(self.EMAIL_REGEX, text)
        return list(set(emails))

    def _extract_phones(self, text: str):
        raw_candidates = re.findall(self.PHONE_CANDIDATE_REGEX, text)
        cleaned = []

        for raw in raw_candidates:
            num = re.sub(r"[^\d+]", "", raw)

            if num.startswith("+420") and len(num) == 13:
                cleaned.append(num)
                continue

            if num.startswith("00420") and len(num) == 14:
                cleaned.append("+" + num[2:])
                continue

            if num.isdigit() and len(num) == 9:
                cleaned.append("+420" + num)
                continue

        return list(set(cleaned))
