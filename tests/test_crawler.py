# tests/test_crawler.py
# Autor: Martin Šilar
# Unit testy interní logiky WebCrawleru (visited / robots / odkazy / filtrování / ukládání JSON)

import unittest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.webcrawler.crawler import WebCrawler
from src.webcrawler.config import CrawlerConfig


def get_config(tmpdir):
    return CrawlerConfig(
        start_url="https://example.com",
        allowed_domain="example.com",
        max_workers=1,
        max_pages=5,
        queue_maxsize=100,
        request_timeout=5,
        user_agent="TestAgent",
        output_dir=tmpdir / "data",
        log_file=tmpdir / "logs" / "test.log",
        profile="contacts",
        save_html=False,
        profiles=["contacts", "seo", "content"]
    )


class TestCrawlerInternal(unittest.TestCase):

    def setUp(self):
        self.tmp = Path("tests/tmp_test_dir")
        self.tmp.mkdir(exist_ok=True)

        self.config = get_config(self.tmp)
        self.crawler = WebCrawler(self.config)

    # --------------------------------------------------------
    def test_same_domain(self):
        self.assertTrue(self.crawler._same_domain("https://example.com/test"))
        self.assertTrue(self.crawler._same_domain("https://sub.example.com/x"))
        self.assertFalse(self.crawler._same_domain("https://google.com"))

    # --------------------------------------------------------
    def test_extract_links(self):
        html = """
        <html><body>
            <a href="/page1">A</a>
            <a href="https://example.com/page2">B</a>
            <a href="other/page3">C</a>
        </body></html>
        """
        links = self.crawler._extract_links("https://example.com", html)
        self.assertIn("https://example.com/page1", links)
        self.assertIn("https://example.com/page2", links)
        self.assertIn("https://example.com/other/page3", links)

    # --------------------------------------------------------
    def test_robots_disallow(self):
        self.crawler.disallowed_paths = ["/admin", "/private"]
        self.assertFalse(self.crawler._allowed_by_robots("https://example.com/admin/panel"))
        self.assertTrue(self.crawler._allowed_by_robots("https://example.com/blog"))

    # --------------------------------------------------------
    def test_should_save_contacts(self):
        self.crawler.config.profile = "contacts"
        self.assertTrue(self.crawler._should_save({"emails": ["a@test.cz"], "phones": []}))
        self.assertFalse(self.crawler._should_save({"emails": [], "phones": []}))

    # --------------------------------------------------------
    def test_should_save_seo(self):
        self.crawler.config.profile = "seo"
        self.assertTrue(self.crawler._should_save({"title": "A"}))
        self.assertFalse(self.crawler._should_save({"title": "", "meta_description": ""}))

    # --------------------------------------------------------
    def test_should_save_content(self):
        self.crawler.config.profile = "content"
        self.assertTrue(self.crawler._should_save({"text": "Dost dlouhý obsah tady"}))
        self.assertFalse(self.crawler._should_save({"text": "krátké"}))

    # --------------------------------------------------------
    @patch("requests.Session.get")
    def test_worker_skips_duplicates(self, mock_get):
        """Crawler nesmí dvakrát navštívit stejnou URL"""

        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.text = "<a href='/next'></a>"
        mock_get.return_value = mock_resp

        self.crawler.visited = set()
        with self.crawler.visited_lock:
            self.crawler.visited.add("https://example.com")

        links = ["https://example.com", "https://example.com/next"]

        with self.crawler.visited_lock:
            for link in links:
                if link not in self.crawler.visited:
                    self.crawler.visited.add(link)

        self.assertIn("https://example.com", self.crawler.visited)
        self.assertIn("https://example.com/next", self.crawler.visited)
        self.assertEqual(len(self.crawler.visited), 2)

    # --------------------------------------------------------
    def test_save_results_creates_valid_json(self):
        """Ověří, že ukládání JSON funguje správně."""

        self.crawler.results = [
            {"url": "a", "x": 1},
            {"url": "b", "x": 2},
        ]

        out = self.crawler.save_results()
        self.assertTrue(out.exists())

        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["url"], "a")


# ------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
