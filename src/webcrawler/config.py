# src/webcrawler/config.py
# Autor: Martin Šilar
# Konfigurace pro multithreaded web crawler

import configparser
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CrawlerConfig:
    start_url: str
    allowed_domain: str
    max_workers: int
    max_pages: int
    queue_maxsize: int
    request_timeout: int
    user_agent: str
    output_dir: Path
    log_file: Path


def load_config(path: str = "config.ini") -> CrawlerConfig:
    cfg = configparser.ConfigParser()
    loaded = cfg.read(path, encoding="utf-8")
    if not loaded:
        raise FileNotFoundError(f"Konfigurační soubor {path} nebyl nalezen")

    c = cfg["crawler"]

    output_dir = Path(c.get("output_dir", "data"))
    log_file = Path(c.get("log_file", "logs/crawler.log"))

    return CrawlerConfig(
        start_url=c.get("start_url"),
        allowed_domain=c.get("allowed_domain"),
        max_workers=c.getint("max_workers", fallback=5),
        max_pages=c.getint("max_pages", fallback=50),
        queue_maxsize=c.getint("queue_maxsize", fallback=1000),
        request_timeout=c.getint("request_timeout", fallback=7),
        user_agent=c.get("user_agent", fallback="WebCrawlerSchoolProject/1.0"),
        output_dir=output_dir,
        log_file=log_file,
    )
