# Multithreaded Web Crawler

Autor: **Martin Šilar**  
Škola: **SPŠE Ječná**  
Ročník: **4.**  
Předmět: **PV – školní projekt (souběžné programování)**  
Kontakt: *silar@spsejecna.cz*  
Datum: **23. 11. 2025**

---

## Popis

Aplikace je vícevláknový web crawler v Pythonu určený pro školní projekt zaměřený na paralelní a souběžné programování.  
Crawler paralelně stahuje stránky v rámci jedné domény, ukládá je na disk a loguje celý průběh.

**Funkce aplikace:**

- prochází web z daného `start_url`
- využívá frontu úloh a architekturu *producer–consumer*
- používá více worker vláken pro souběžné zpracování
- ukládá stažené HTML soubory do složky `data/`
- loguje průběh do souboru `logs/crawler.log`
- respektuje povolenou doménu (`allowed_domain`) a limit počtu stažených stránek (`max_pages`)

---

## Architektura

### Struktura projektu

```
webcrawler-project/
├── config.ini
├── requirements.txt
├── README.md
├── .gitignore
├── doc
│   └── documentation.md
├── src/
│   ├── main.py
│   └── webcrawler/
│       ├── __init__.py
│       ├── config.py
│       └── crawler.py
├── data/      (automaticky vytvořeno)
└── logs/      (automaticky vytvořeno)
```

### Hlavní komponenty

- **main.py** – vstupní bod programu, načítá konfiguraci a spouští crawler.
- **crawler.py** – logika vícevláknového zpracování:
    - fronta úloh (`task_queue`)
    - fronta logů (`log_queue`)
    - worker vlákna
    - logger vlákno
    - extrakce a filtrování odkazů
- **config.py** – načítání konfigurace z `config.ini` pomocí datové třídy `CrawlerConfig`.

### Paralelní model

Aplikace používá model **producer–consumer**:

- hlavní vlákno vloží počáteční URL do `task_queue`
- worker vlákna paralelně:
    - odebírají URL z fronty
    - stahují HTML
    - extrahují nové odkazy
    - přidávají další úlohy do fronty
- logger vlákno zapisuje logy z `log_queue` (aby nedocházelo ke konfliktům o soubor)

---

## Konfigurace (config.ini)

```
[crawler]
start_url = https://example.com
allowed_domain = example.com

max_workers = 5
max_pages = 50
queue_maxsize = 1000

request_timeout = 7
user_agent = WebCrawlerSchoolProject/1.0

output_dir = data
log_file = logs/crawler.log
```

### Význam jednotlivých voleb

- **start_url** – počáteční stránka, kterou crawler stáhne jako první
- **allowed_domain** – doména, ve které se crawler smí pohybovat
- **max_workers** – počet worker vláken
- **max_pages** – limit počtu stažených stránek
- **queue_maxsize** – maximální počet URL ve frontě úloh
- **request_timeout** – timeout pro HTTP požadavky
- **user_agent** – identifikace crawleru v HTTP hlavičce
- **output_dir** – umístění stažených HTML
- **log_file** – umístění log souboru

---

## Instalace

### 1) Předpoklady

- Python **3.x**
- internetové připojení (pokud cílový web není lokální)
- možnost použít `pip install`

### 2) Instalace závislostí

```bash
pip install -r requirements.txt
```

---

## Spuštění

Z kořenové složky:

```bash
python src/main.py
```

Spuštění s vlastní konfigurací:

```bash
python src/main.py muj_config.ini
```

---

## Chybové stavy

Program řeší běžné situace:

- **Timeout při stahování**  
  uloží chybu do logu, pokračuje dále

- **HTTP chyby (404, 500, ...)**  
  zaloguje, pokračuje

- **Nemožnost zapsat do souboru**  
  zaloguje `[SAVE][ERROR]`, úloha se přeskočí

- **Konfigurační soubor nenalezen**  
  program se ukončí s jasnou chybovou hláškou

- **Přetečení fronty úloh**  
  URL je přeskočeno, zalogováno jako varování

---

## Testování

### Provedené testy:

- test s jednoduchým webem (`example.com`)
- test s vícestránkovým webem (`python.org`)
- test malého limitu (`max_pages = 3`)
- test neexistující domény (ověření robustnosti)
- test chování front a správného ukončení workerů

### Výsledek:

Aplikace splňuje zadání – paralelní crawling, omezení domény, model producer–consumer, synchronizace sdílených dat, konfigurovatelnost a robustní ošetření chyb.

---

## Licence a právní aspekty

- Projekt vznikl jako **školní práce**.
- Knihovny:
    - `requests` – licence Apache 2.0
    - `beautifulsoup4` – licence MIT
- Crawler je určen pro legální procházení webů; uživatel je zodpovědný za respektování podmínek cílového serveru.

---

## Známé bugy a plán rozšíření

### Známé omezení
- extrakce odkazů pouze z `<a href>` – ignoruje JS navigaci
- seznam navštívených URL je pouze v paměti

### Možný rozvoj
- ukládat metadata (status code, velikost)
- napojení na databázi
- implementovat webové UI pro kontrolu průběhu

---

