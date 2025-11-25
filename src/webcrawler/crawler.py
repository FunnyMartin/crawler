# src/webcrawler/crawler.py
# Autor: Martin Šilar
# Multithreaded Web Crawler – verze s progress barem

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
        self.config = config

        self.task_queue: Queue = Queue(maxsize=self.config.queue_maxsize)
        self.log_queue: Queue = Queue()

        self.visited = set()
        self.visited_lock = threading.Lock()

        self.page_count = 0
        self.page_count_lock = threading.Lock()

        self.ui_status = ""
        self.ui_lock = threading.Lock()

        self._finished = False

        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.domain = self.config.allowed_domain
        self.disallowed_paths, self.crawl_delay = self._load_robots_txt()

    # ---------------- LOGGING ----------------

    def log(self, msg: str):
        self.log_queue.put(msg)

    def logger_thread(self):
        with self.config.log_file.open("a", encoding="utf-8") as f:
            while True:
                msg = self.log_queue.get()
                try:
                    if msg is LOG_SENTINEL:
                        break
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    line = f"{timestamp} | {msg}"
                    f.write(line + "\n")
                    f.flush()
                finally:
                    self.log_queue.task_done()

    # ------------ UI STATUS ------------

    def update_status(self, text: str):
        with self.ui_lock:
            self.ui_status = text

    # ---------------- WORKER ----------------

    def worker_thread(self, worker_id: int):
        self.log(f"[WORKER-{worker_id}] Start")
        session = requests.Session()
        session.headers.update({"User-Agent": self.config.user_agent})

        while True:
            url = self.task_queue.get()

            if url is JOB_SENTINEL:
                self.log(f"[WORKER-{worker_id}] Dostal sentinel, končím.")
                self.task_queue.task_done()
                break

            self.update_status(f"Stahuji: {url}")

            if self.crawl_delay > 0:
                time.sleep(self.crawl_delay)

            with self.page_count_lock:
                if self.page_count >= self.config.max_pages:
                    self.task_queue.task_done()
                    continue
                self.page_count += 1
                index = self.page_count

            try:
                resp = session.get(url, timeout=self.config.request_timeout)
                resp.raise_for_status()
                html = resp.text
            except Exception as e:
                self.log(f"[WORKER-{worker_id}] ERROR {url}: {e}")
                self.update_status(f"Chyba: {url}")
                self.task_queue.task_done()
                continue

            if self.config.save_html:
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
                    except:
                        pass

            self.update_status(f"Hotovo: {url}")
            self.task_queue.task_done()

        session.close()

    # ---------------- ROBOTS ----------------

    def _load_robots_txt(self):
        url = f"https://{self.domain}/robots.txt"
        disallowed = []
        delay = 0
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return [], 0

            for line in r.text.splitlines():
                line = line.strip().lower()
                if line.startswith("disallow:"):
                    rule = line.split(":", 1)[1].strip()
                    disallowed.append(rule)
                if line.startswith("crawl-delay:"):
                    try:
                        delay = float(line.split(":", 1)[1].strip())
                    except:
                        delay = 0
        except:
            return [], 0

        return disallowed, delay

    def _allowed_by_robots(self, url):
        path = urlparse(url).path
        for r in self.disallowed_paths:
            if r == "/":
                return False
            if path.startswith(r):
                return False
        return True

    def _same_domain(self, url):
        host = urlparse(url).netloc
        return host == self.domain or host.endswith("." + self.domain)

    # ---------------- HTML ----------------

    def _extract_links(self, base_url, html):
        soup = BeautifulSoup(html, "html.parser")
        out = []
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            abs_url = urljoin(base_url, href)
            cleaned = urlparse(abs_url)._replace(fragment="").geturl()
            out.append(cleaned)
        return out

    def _safe_filename(self, index, url):
        parsed = urlparse(url)
        path = parsed.path.strip("/") or "index"
        path = path.replace("/", "_")
        if len(path) > 50:
            path = path[:50]
        return f"{index:04d}_{path}.html"

    def _save_page(self, url, html, index):
        file = self.config.output_dir / self._safe_filename(index, url)
        try:
            with file.open("w", encoding="utf-8") as f:
                f.write(f"<!-- URL: {url} -->\n")
                f.write(html)
        except Exception as e:
            self.log(f"[SAVE][ERROR] {url}: {e}")

    # ---------------- RUN LOGIC ----------------

    def start_async(self):
        self._finished = False

        logger = threading.Thread(target=self.logger_thread, daemon=False)
        logger.start()
        self._logger_thread = logger

        workers = []
        for i in range(self.config.max_workers):
            t = threading.Thread(target=self.worker_thread, args=(i + 1,))
            t.start()
            workers.append(t)
        self._workers = workers

        with self.visited_lock:
            self.visited.add(self.config.start_url)

        self.task_queue.put(self.config.start_url)

    def wait(self):
        self.task_queue.join()

        for _ in range(self.config.max_workers):
            self.task_queue.put(JOB_SENTINEL)

        for t in self._workers:
            t.join()

        self.log_queue.put(LOG_SENTINEL)
        self.log_queue.join()
        self._logger_thread.join()

        self._finished = True

    def is_running(self):
        return not self._finished
