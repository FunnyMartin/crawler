# Multithreaded Web Crawler

Autor: **Martin Šilar**  
Škola: **SPŠE Ječná**  
Předmět: **PV – souběžné programování**  
Datum: **30. 11. 2025**

---

## Přehled

Aplikace je vícevláknový web crawler, který již neslouží pouze ke stahování HTML, ale provádí **cílenou těžbu dat** podle zvoleného profilu:

- kontakty (e-maily + validní mezinárodní telefonní čísla),
- SEO metadata,
- textový obsah stránky.

HTML lze volitelně ukládat. Extrahovaná data se ukládají jako JSON.

Součástí projektu jsou:

- vícevláknová architektura (producer–consumer),
- konzolové menu,
- extraktory dat,
- logování do souboru,
- robustní práce s chybami,
- jednotkové testy + uživatelské testování.

---

## Funkce

### **Crawling**
- paralelní zpracování pomocí worker vláken
- fronty URL + fronty logů
- respektování `robots.txt` (crawl-delay, disallow)
- filtrace domény
- limit navštívených stránek

### **Profily těžby dat**

#### `contacts`
- extrakce e-mailů
- extrakce telefonních čísel (jen formát +XXX…)

#### `seo`
- title
- meta description
- meta keywords
- nadpisy H1–H3

#### `content`
- očištěný text (bez HTML tagů)

#### `custom`
- uloží všechna extrahovaná data bez filtrace (v budoucnosti)

### **Volitelné ukládání HTML**
Zapíná se a vypíná přímo v menu.

---

## Struktura projektu

```
project/
├── config.ini
├── requirements.txt
├── README.md
├── doc/
│   ├── documentation.md
│   └── user_testing_report.pdf
├── tests/
│   └── test_extractors.py
├── src/
│   ├── main.py
│   ├── __init__.py
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── exit_app.py
│   │   ├── run_crawler.py
│   │   ├── set_profile.py
│   │   ├── show_config.py
│   │   ├── show_profiles.py
│   │   └── toggle_save_html.py
│   └── webcrawler/
│       ├── __init__.py
│       ├── config.py
│       ├── crawler.py
│       ├── base_extractor.py
│       ├── contacts_extractor.py
│       ├── seo_extractor.py
│       └── content_extractor.py
├── data/ (generuje se)
└── logs/ (generuje se)
```


---

## Konfigurace (`config.ini`)

```ini
[crawler]
start_url = https://priklad.cz
allowed_domain = priklad.cz

max_workers = 5
max_pages = 50
queue_maxsize = 1000

request_timeout = 7
user_agent = WebCrawlerSchoolProject/1.0

output_dir = data
log_file = logs/crawler.log

profiles = contacts, seo, content
profile = contacts
save_html = false
```

## Instalace
```bash
pip install -r requirements.txt
```

---

## Spuštění programu

Projekt se nespouští přímo pomocí `python src/main.py`, protože používá balíčkovou strukturu.  
Správný způsob je spouštět ho jako **modul**:

```bash
python -m src.main
```

## Spuštění s jiným konfiguračním souborem
```bash
python -m src.main muj_config.ini
```
