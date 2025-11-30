# tests/test_crawler_helpers.py
# Autor: Martin Šilar
# Unit testy pomocných metod WebCrawleru

import unittest
from pathlib import Path
from unittest.mock import patch

from src.webcrawler.config import CrawlerConfig
from src.webcrawler.crawler import WebCrawler


def _make_test_config():
    """Vytvoří jednoduchou testovací konfiguraci."""
    return CrawlerConfig(
        start_url="https://example.com",
        allowed_domain="example.com",
        max_workers=2,
        max_pages=50,
        queue_maxsize=100,
        request_timeout=5,
        user_agent="TestAgent/1.0",
        output_dir=Path("test_data"),
        log_file=Path("logs/test.log"),
        profile="contacts",
        save_html=False,
        profiles=["contacts", "seo", "content"],
    )


class TestCrawlerHelpers(unittest.TestCase):
    def setUp(self):
        config = _make_test_config()
        with patch.object(WebCrawler, "_load_robots_txt", return_value=([], 0)):
            self.crawler = WebCrawler(config)

    def test_same_domain_exact(self):
        self.assertTrue(self.crawler._same_domain("https://example.com/page"))

    def test_same_domain_subdomain(self):
        self.assertTrue(self.crawler._same_domain("https://sub.example.com/abc"))

    def test_same_domain_other_domain(self):
        self.assertFalse(self.crawler._same_domain("https://other.com"))

    def test_allowed_by_robots_empty_rules(self):
        self.crawler.disallowed_paths = []
        self.assertTrue(self.crawler._allowed_by_robots("https://example.com/test"))

    def test_allowed_by_robots_root_blocked(self):
        self.crawler.disallowed_paths = ["/"]
        self.assertFalse(self.crawler._allowed_by_robots("https://example.com/test"))

    def test_allowed_by_robots_prefix_blocked(self):
        self.crawler.disallowed_paths = ["/admin"]
        self.assertFalse(self.crawler._allowed_by_robots("https://example.com/admin/panel"))
        self.assertTrue(self.crawler._allowed_by_robots("https://example.com/public"))

    def test_extract_links_basic(self):
        html = """
        <html>
          <body>
            <a href="/page1">One</a>
            <a href="https://example.com/page2#section">Two</a>
            <a href="https://other.com/x">Other</a>
          </body>
        </html>
        """
        links = self.crawler._extract_links("https://example.com", html)

        self.assertIn("https://example.com/page1", links)
        self.assertIn("https://example.com/page2", links)
        self.assertIn("https://other.com/x", links)

    def test_should_save_contacts_profile_requires_email_or_phone(self):
        self.crawler.config.profile = "contacts"

        self.assertFalse(self.crawler._should_save({"url": "x"}))
        self.assertTrue(self.crawler._should_save({"url": "x", "emails": ["a@test.com"]}))
        self.assertTrue(self.crawler._should_save({"url": "x", "phones": ["+420123456789"]}))
        self.assertTrue(self.crawler._should_save({"url": "x", "emails": [], "phones": ["+420123"]}))

    def test_should_save_seo_profile_requires_title_or_description(self):
        self.crawler.config.profile = "seo"

        self.assertFalse(self.crawler._should_save({"url": "x"}))
        self.assertTrue(self.crawler._should_save({"url": "x", "title": "Test"}))
        self.assertTrue(self.crawler._should_save({"url": "x", "meta_description": "Desc"}))

    def test_should_save_content_profile_requires_longer_text(self):
        self.crawler.config.profile = "content"

        self.assertFalse(self.crawler._should_save({"url": "x", "text": "krátké"}))
        self.assertTrue(self.crawler._should_save({"url": "x", "text": "Tady je delší text, který má víc než dvacet znaků."}))

    def test_should_save_custom_profile_always_true(self):
        self.crawler.config.profile = "custom"
        self.assertTrue(self.crawler._should_save({"url": "x"}))


if __name__ == "__main__":
    unittest.main()
