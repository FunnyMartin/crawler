# tests/test_extractors.py
# Autor: Martin Šilar
# Unit testy extractorů (contacts / seo / content)

import unittest

from src.webcrawler.contacts_extractor import ContactsExtractor
from src.webcrawler.seo_extractor import SEOExtractor
from src.webcrawler.content_extractor import ContentExtractor


class TestContactsExtractor(unittest.TestCase):
    def setUp(self):
        self.ext = ContactsExtractor()

    def test_extracts_email_and_international_phone(self):
        html = """
        <html>
          <body>
            Kontakt: info@test.cz, tel: +420 777 123 456,
            a nějaký šum 123456.
          </body>
        </html>
        """
        result = self.ext.extract("https://example.com/kontakt", html)

        self.assertEqual(result["url"], "https://example.com/kontakt")
        self.assertIn("info@test.cz", result["emails"])

        for phone in result["phones"]:
            self.assertTrue(phone.startswith("+"))

        self.assertTrue(any(p.startswith("+420") for p in result["phones"]))

    def test_no_contacts_returns_none(self):
        html = "<html><body><p>Žádné kontakty zde nejsou.</p></body></html>"
        result = self.ext.extract("http://test.com", html)
        self.assertIsNone(result)


class TestSEOExtractor(unittest.TestCase):
    def setUp(self):
        self.ext = SEOExtractor()

    def test_extracts_basic_seo_fields(self):
        html = """
        <html>
            <head>
                <title>Test Title</title>
                <meta name="description" content="Popis stránky">
            </head>
            <body>
                <h1>Nadpis</h1>
            </body>
        </html>
        """

        result = self.ext.extract("http://test.com", html)

        self.assertEqual(result["url"], "http://test.com")
        self.assertEqual(result["title"], "Test Title")
        self.assertEqual(result["meta_description"], "Popis stránky")
        self.assertEqual(result["meta_keywords"], [])
        self.assertEqual(result["headings"], ["Nadpis"])


class TestContentExtractor(unittest.TestCase):
    def setUp(self):
        self.ext = ContentExtractor()

    def test_extracts_plain_text_without_tags(self):
        html = """
        <html>
          <body>
            <h1>Nadpis</h1>
            <p>První odstavec.</p>
            <p>Druhý odstavec.</p>
          </body>
        </html>
        """
        result = self.ext.extract("https://example.com/content", html)

        self.assertEqual(result["url"], "https://example.com/content")
        text = result["text"]

        self.assertIn("Nadpis", text)
        self.assertIn("První odstavec.", text)
        self.assertIn("Druhý odstavec.", text)

        self.assertNotIn("<h1>", text)
        self.assertNotIn("<p>", text)


if __name__ == "__main__":
    unittest.main()
