# src/webcrawler/crawler.py
# Autor: Martin Šilar
# Multithreaded web crawler – školní projekt (producer–consumer, synchronizace, fronty)

import threading
from queue import Queue
from pathlib import Path
from urllib.parse import urljoin, urlparse
import time

import requests
from bs4 import BeautifulSoup

from .config import CrawlerConfig

JOB_SENTINEL = object()
LOG_SENTINEL = object()


class WebCrawler:
    def __init__(self, config: CrawlerConfig):
        """Inicializace crawleru: příprava front, sdílených struktur, zámků a načtení robots.txt."""
        self.config = config

        self.task_queue: Queue = Queue(maxsize=self.config.queue_maxsize)
        self.log_queue: Queue = Queue()

        self.visited = set()
        self.visited_lock = threading.Lock()

        self.page_count = 0
        self.page_count_lock = threading.Lock()

        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.domain = self.config.allowed_domain

        self.disallowed_paths, self.crawl_delay = self._load_robots_txt()

    # ---------- Logging ----------

    def log(self, msg: str):
        """Vloží zprávu do logovací fronty."""
        self.log_queue.put(msg)

    def logger_thread(self):
        """Samostatné vlákno pro sekvenční zapisování logů do souboru i na konzoli."""
        with self.config.log_file.open("a", encoding="utf-8") as f:
            while True:
                msg = self.log_queue.get()
                try:
                    if msg is LOG_SENTINEL:
                        break
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    line = f"{timestamp} | {msg}"
                    print(line)
                    f.write(line + "\n")
                    f.flush()
                finally:
                    self.log_queue.task_done()
        print("[LOGGER] Ukončen.")

    # ---------- Worker ----------

    def worker_thread(self, worker_id: int):
        """Worker vlákno: stahuje URL, ukládá stránky, extrahuje odkazy a přidává nové úlohy."""
        self.log(f"[WORKER-{worker_id}] Start")
        session = requests.Session()
        session.headers.update({"User-Agent": self.config.user_agent})

        while True:
            url = self.task_queue.get()

            if url is JOB_SENTINEL:
                self.log(f"[WORKER-{worker_id}] Dostal sentinel, končím.")
                self.task_queue.task_done()
                break

            if self.crawl_delay > 0:
                time.sleep(self.crawl_delay)

            with self.page_count_lock:
                if self.page_count >= self.config.max_pages:
                    self.task_queue.task_done()
                    continue
                self.page_count += 1
                index = self.page_count

            self.log(f"[WORKER-{worker_id}] Fetch {url} ({index}/{self.config.max_pages})")

            try:
                resp = session.get(url, timeout=self.config.request_timeout)
                resp.raise_for_status()
                html = resp.text
            except Exception as e:
                self.log(f"[WORKER-{worker_id}] ERROR {url}: {e}")
                self.task_queue.task_done()
                continue

            self._save_page(url, html, index)

            links = self._extract_links(url, html)

            with self.visited_lock:
                for link in links:
                    if link in self.visited:
                        continue
                    if not self._same_domain(link):
                        continue
                    if not self._allowed_by_robots(link):
                        continue
                    if self.page_count >= self.config.max_pages:
                        break

                    self.visited.add(link)
                    try:
                        self.task_queue.put_nowait(link)
                    except Exception:
                        self.log(f"[WORKER-{worker_id}] Warning: fronta je plná, odkaz zahazuji")

            self.log(f"[WORKER-{worker_id}] Done {url}")
            self.task_queue.task_done()

        session.close()
        self.log(f"[WORKER-{worker_id}] Ukončen.")

    # ---------- Pomocné metody ----------

    def _load_robots_txt(self):
        """Načte soubor robots.txt a vrací seznam zakázaných cest a případné crawl-delay."""
        domain_root = f"https://{self.domain}"
        robots_url = domain_root + "/robots.txt"
        disallowed = []
        crawl_delay = 0

        try:
            session = requests.Session()
            session.headers.update({"User-Agent": self.config.user_agent})
            response = session.get(robots_url, timeout=5)

            if response.status_code != 200:
                return disallowed, 0

            for line in response.text.splitlines():
                line = line.strip().lower()

                if line.startswith("disallow:"):
                    rule = line.split(":", 1)[1].strip()
                    if rule:
                        disallowed.append(rule)

                if line.startswith("crawl-delay:"):
                    delay_str = line.split(":", 1)[1].strip()
                    try:
                        crawl_delay = float(delay_str)
                    except:
                        crawl_delay = 0

            return disallowed, crawl_delay

        except Exception:
            return [], 0

    def _allowed_by_robots(self, url: str) -> bool:
        """Vrací True, pokud URL není blokována direktivami Disallow v robots.txt."""
        parsed = urlparse(url)
        path = parsed.path

        for rule in self.disallowed_paths:
            if rule == "/":
                return False
            if path.startswith(rule):
                return False
        return True

    def _same_domain(self, url: str) -> bool:
        """Testuje, zda URL patří do povolené domény."""
        host = urlparse(url).netloc
        return host == self.domain or host.endswith("." + self.domain)

    def _extract_links(self, base_url: str, html: str):
        """Z HTML extrahuje všechny odkazy <a href> a převádí je na absolutní URL."""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            abs_url = urljoin(base_url, href)
            parsed = urlparse(abs_url)
            cleaned = parsed._replace(fragment="").geturl()
            links.append(cleaned)
        return links

    def _safe_filename(self, index: int, url: str) -> str:
        """Vytvoří bezpečný název souboru z URL a pořadového čísla."""
        parsed = urlparse(url)
        path = parsed.path.strip("/") or "index"
        path = path.replace("/", "_")
        if len(path) > 50:
            path = path[:50]
        return f"{index:04d}_{path}.html"

    def _save_page(self, url: str, html: str, index: int):
        """Uloží HTML stránku na disk do adresáře output_dir."""
        filename = self._safe_filename(index, url)
        filepath: Path = self.config.output_dir / filename
        try:
            with filepath.open("w", encoding="utf-8") as f:
                f.write(f"<!-- URL: {url} -->\n")
                f.write(html)
        except Exception as e:
            self.log(f"[SAVE][ERROR] {url} -> {filepath}: {e}")

    # ---------- Spuštění ----------

    def run(self):
        """Hlavní běh crawleru: spustí logger, workery, vloží startovací URL a řídí ukončení vláken."""
        logger = threading.Thread(target=self.logger_thread, daemon=False)
        logger.start()

        workers = []
        for i in range(self.config.max_workers):
            t = threading.Thread(target=self.worker_thread, args=(i + 1,), daemon=False)
            t.start()
            workers.append(t)

        with self.visited_lock:
            self.visited.add(self.config.start_url)

        self.task_queue.put(self.config.start_url)
        self.log(f"[MAIN] Start URL: {self.config.start_url}")

        self.task_queue.join()

        for _ in range(self.config.max_workers):
            self.task_queue.put(JOB_SENTINEL)

        for t in workers:
            t.join()

        self.log_queue.put(LOG_SENTINEL)
        self.log_queue.join()
        logger.join()

        print("Crawling dokončeno.")
