# src/webcrawler/crawler.py
# Autor: Martin Šilar
# Multithreaded Web Crawler – těžba dat (contacts / seo / content)

import threading
import time
import json
from queue import Queue
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .base_extractor import BaseExtractor


JOB_SENTINEL = object()
LOG_SENTINEL = object()


class WebCrawler:
    def __init__(self, config):
        self.config = config

        self.task_queue = Queue(maxsize=self.config.queue_maxsize)
        self.log_queue = Queue()

        self.visited = set()
        self.visited_lock = threading.Lock()

        self.page_count = 0
        self.page_count_lock = threading.Lock()

        self.active_workers = 0
        self.active_workers_lock = threading.Lock()

        self.finished_early = False

        self.results = []
        self.extractor: BaseExtractor | None = None

        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.domain = self.config.allowed_domain
        self.disallowed_paths, self.crawl_delay = self._load_robots_txt()

    def set_extractor(self, extractor: BaseExtractor):
        self.extractor = extractor
        extractor.set_crawler(self)

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
                    f.write(f"{timestamp} | {msg}\n")
                    f.flush()
                finally:
                    self.log_queue.task_done()

    def worker_thread(self, wid: int):
        self.log(f"[WORKER-{wid}] Start worker")

        session = requests.Session()
        session.headers.update({"User-Agent": self.config.user_agent})

        while True:
            url = self.task_queue.get()

            if url is JOB_SENTINEL:
                self.task_queue.task_done()
                break

            with self.active_workers_lock:
                self.active_workers += 1

            try:
                if self.crawl_delay > 0:
                    time.sleep(self.crawl_delay)

                with self.page_count_lock:
                    if self.page_count >= self.config.max_pages:
                        continue
                    self.page_count += 1
                    index = self.page_count

                try:
                    resp = session.get(url, timeout=self.config.request_timeout)
                    resp.raise_for_status()
                    html = resp.text
                except Exception as e:
                    self.log(f"[WORKER-{wid}] ERROR {url}: {e}")
                    continue

                if self.extractor:
                    extracted = None
                    try:
                        extracted = self.extractor.extract(url, html)
                    except Exception as e:
                        self.log(f"[WORKER-{wid}] EXTRACT ERROR {url}: {e}")

                    if self._should_save(extracted):
                        self.results.append(extracted)

                if self.config.save_html:
                    self._save_page(index, url, html)

                links = self._extract_links(url, html)

                with self.visited_lock:
                    for link in links:
                        if link in self.visited:
                            continue
                        if not self._same_domain(link):
                            continue
                        if not self._allowed_by_robots(link):
                            continue
                        self.visited.add(link)
                        try:
                            self.task_queue.put_nowait(link)
                        except:
                            pass

            finally:
                with self.active_workers_lock:
                    self.active_workers -= 1
                self.task_queue.task_done()

        session.close()
        self.log(f"[WORKER-{wid}] Ukončen.")

    def _should_save(self, data: dict | None) -> bool:
        if not data:
            return False

        profile = self.config.profile

        if profile == "contacts":
            return bool(data.get("emails")) or bool(data.get("phones"))

        if profile == "seo":
            return bool(data.get("title")) or bool(data.get("meta_description"))

        if profile == "content":
            text = data.get("text", "").strip()
            return len(text) > 20

        return True

    def _load_robots_txt(self):
        root = f"https://{self.domain}/robots.txt"
        disallowed = []
        delay = 0

        try:
            resp = requests.get(root, timeout=5)
            if resp.status_code != 200:
                return [], 0

            for line in resp.text.splitlines():
                line = line.strip().lower()

                if line.startswith("disallow:"):
                    rule = line.split(":", 1)[1].strip()
                    if rule:
                        disallowed.append(rule)

                if line.startswith("crawl-delay:"):
                    try:
                        delay = float(line.split(":", 1)[1].strip())
                    except:
                        delay = 0

            return disallowed, delay

        except Exception:
            return [], 0

    def _allowed_by_robots(self, url: str) -> bool:
        path = urlparse(url).path
        for rule in self.disallowed_paths:
            if rule == "/" or path.startswith(rule):
                return False
        return True

    def _same_domain(self, url: str) -> bool:
        host = urlparse(url).netloc
        return host == self.domain or host.endswith("." + self.domain)

    def _extract_links(self, base, html):
        soup = BeautifulSoup(html, "html.parser")
        out = []
        for a in soup.find_all("a", href=True):
            abs_url = urljoin(base, a["href"])
            cleaned = urlparse(abs_url)._replace(fragment="").geturl()
            out.append(cleaned)
        return out

    def _safe_filename(self, index, url):
        parsed = urlparse(url)
        path = parsed.path.strip("/") or "index"
        path = path.replace("/", "_")[:50]
        return f"{index:04d}_{path}.html"

    def _save_page(self, index, url, html):
        fpath = self.config.output_dir / self._safe_filename(index, url)
        try:
            with fpath.open("w", encoding="utf-8") as f:
                f.write(f"<!-- URL: {url} -->\n")
                f.write(html)
        except:
            pass

    def run(self):
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

        while True:
            time.sleep(0.2)
            with self.active_workers_lock:
                active = self.active_workers
            if self.task_queue.empty() and active == 0:
                break

        if self.page_count < self.config.max_pages:
            self.finished_early = True

        for _ in workers:
            self.task_queue.put(JOB_SENTINEL)

        for t in workers:
            t.join()

        self.log_queue.put(LOG_SENTINEL)
        self.log_queue.join()
        logger.join()

    def save_results(self):
        output_path = self.config.output_dir / f"{self.config.profile}_data.json"
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        return output_path
