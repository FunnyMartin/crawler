# Multithreaded Web Crawler – dokumentace

Autor: **Martin Šilar**  
Škola: **SPŠE Ječná**  
Ročník: **4.**  
Předmět: **PV – školní projekt (souběžné programování)**  
Kontakt: *silar@spsejecna.cz*  
Datum vypracování: **30. 11. 2025**

---

## 1. Název a účel projektu

**Název projektu:** Multithreaded Web Crawler

**Stručný popis:**  
Projekt je vícevláknový webový crawler napsaný v Pythonu. Paralelně prochází web v rámci jedné domény, zpracovává stránky a podle zvoleného profilu z nich těží strukturovaná data. Aplikace využívá architekturu *producer–consumer*, více pracovních vláken, samostatné logovací vlákno, a konfigurační soubor, který umožňuje měnit chování programu bez zásahu do kódu.

**Účel projektu:**  
Ukázat praktické využití paralelního zpracování, front úloh, synchronizace vláken a ETL principů na reálném problému – automatickém sběru dat z webu.  
Aktuální verze se zaměřuje na **těžbu dat (data mining)**: kontakty, SEO informace nebo textový obsah, nikoliv již jen na ukládání HTML.

---

## 2. Požadavky uživatele

### 2.1 Funkční požadavky

1. Nastavení počáteční URL (start_url), ze které crawler začíná.
2. Procházení pouze v rámci jedné domény (allowed_domain).
3. Použití více worker vláken pro paralelní stahování.
4. Čtení konfigurace ze souboru `config.ini`.
5. Těžba dat podle zvoleného profilu:
    - **contacts** – e-maily, telefonní čísla
    - **seo** – title, meta popis, nadpisy
    - **content** – čistý textový obsah
6. Volitelné ukládání HTML (save_html).
7. Ukládání výstupních dat do JSON.
8. Zapisování logů pomocí samostatného logovacího vlákna.
9. Spuštění z příkazové řádky.

### 2.2 Nefunkční požadavky

- efektivní paralelní provádění
- respektování robots.txt (Disallow, Crawl-delay)
- odolnost vůči chybám (timeouty, HTTP chyby)
- neztrátová synchronizace nad sdílenými strukturami
- přehledné a udržovatelné rozložení kódu do modulů
- přenositelnost (Python 3.x + pip instalace)

### 2.3 Respektování robots.txt

Podporované direktivy:

- **Disallow:** URL, jejichž cesta odpovídá pravidlu, nejsou nikdy zpracovány
- **Crawl-delay:** časová prodleva mezi požadavky

Tento mechanismus zajišťuje bezpečný a etický běh crawleru.

### 2.4 Use Case – slovní popis

Aktér: uživatel/student  
Cíl: stáhnout část webu nebo z něj vytěžit strukturovaná data

Postup:
1. Uživatel upraví config.ini.
2. Spustí program:
   ```
   python -m src.main
   ```
3. Vybere režim v textovém menu.
4. Crawler paralelně stahuje stránky a těží data podle profilu.
5. Data se uloží do JSON (`data/<profil>_data.json`).
6. Logy se zapíší do `logs/crawler.log`.

---

## 3. Architektura aplikace

### 3.1 Moduly a soubory

- **src/main.py**  
  Konzolové uživatelské rozhraní + Command pattern.

- **src/webcrawler/config.py**  
  Načítání konfigurace do datové třídy `CrawlerConfig`.

- **src/webcrawler/crawler.py**  
  Jádro programu – vícevláknový crawler, fronty, extrakce, ukládání výsledků.

- **src/webcrawler/base_extractor.py**  
  Základní třída pro extraktory (strategy pattern).

- **src/webcrawler/contacts_extractor.py**  
  Extrakce e-mailů a telefonů.

- **src/webcrawler/seo_extractor.py**  
  Title, meta popisy, H1–H6.

- **src/webcrawler/content_extractor.py**  
  Čistý text blogů, článků a obsahových webů.

### 3.2 Architektonický princip

Schéma běhu:

- main vybere profil a vytvoří vhodný extractor
- WebCrawler vytvoří worker a logger vlákna
- start_url je vložena do `task_queue`
- workery:
    - stáhnou HTML
    - aplikují extractor
    - nalezené odkazy opět vkládají do fronty
- logger sériově zapisuje logy
- po dokončení úloh se pošlou sentinely
- výsledná data se uloží do JSON

### 3.3 Command Pattern – modul `src/commands/`

Aplikace používá **Command pattern** pro všechny operace dostupné v hlavním menu.  
Každá položka menu je samostatná třída s metodou `execute()`.  
To zpřehledňuje kód, umožňuje snadné rozšiřování a testování.

#### `base.py` — abstraktní příkaz
Základní abstraktní třída pro všechny commands.

- definuje metodu `execute()`, kterou musí implementovat každý command
- poskytuje jednotnou strukturu pro menu

#### `exit_app.py` — ukončení aplikace
- vypíše hlášku
- ukončí běh programu pomocí `exit(0)`

Použití:  
Menu volba „Konec“.

#### `run_crawler.py` — spuštění crawleru
- načte konfiguraci
- vytvoří instanci WebCrawler
- podle profilu vybere správný extractor
- nastaví extractor do crawleru
- zobrazuje průběh pomocí tqdm progress baru
- spustí crawler ve více vláknech
- po dokončení uloží výsledky do JSON

#### `set_profile.py` — změna profilu těžby
- umožňuje přepnout mezi:
    - contacts
    - seo
    - content
    - custom
- zapíše změnu do `config.ini`
- změna se projeví při dalším spuštění crawleru

#### `show_config.py` — zobrazení aktuální konfigurace
- vypíše všechny aktuální parametry konfigurace  
  (start_url, doména, profil těžby, ukládání HTML, limity, počty vláken)

#### `show_profiles.py` — zobrazení dostupných profilů
- načte seznam profilů ze `config.profiles`
- vypíše je uživateli

#### `toggle_save_html.py` — zapnutí/vypnutí ukládání HTML
- přepne boolean hodnotu `save_html`
- zapíše změnu do `config.ini`



### 3.4 Struktura Command Patternu v projektu

```
src/
├── commands/
│   ├── __init__.py
│   ├── base.py                → abstraktní Command
│   ├── exit_app.py            → ukončení programu
│   ├── run_crawler.py         → spuštění crawleru + progress bar
│   ├── set_profile.py         → změna těžebního profilu
│   ├── show_config.py         → výpis konfigurace
│   ├── show_profiles.py       → dostupné profily
│   └── toggle_save_html.py    → přepnutí ukládání HTML
│
├── webcrawler/
│   ├── __init__.py
│   ├── config.py              → načtení konfigurace
│   ├── crawler.py             → vícevláknový crawler
│   ├── base_extractor.py      → společná logika extraktorů
│   ├── contacts_extractor.py  → extrakce emailů / telefonů
│   ├── seo_extractor.py       → extrakce title / meta / headings
│   └── content_extractor.py   → extrakce textového obsahu
│
└── main.py                    → menu aplikace + mapování commandů
```


### 3.5 Shrnutí přínosu Command Patternu

- odděluje logiku UI (menu) od logiky programu
- modulární rozšíření (nový příkaz = nový soubor)
- jednotlivé příkazy jsou izolované → snadno testovatelné
- hlavní menu je přehledné, bez podmínek a dlouhých funkcí


---

## 4. Popis běhu aplikace

### 4.1 Typický běh

1. Uživatel spustí program přes `python -m src.main`.
2. Zvolí v menu režim těžby.
3. Vloží se startovní URL.
4. Paralelní stahování a těžba probíhá, progress bar zobrazuje stav.
5. Výsledky se ukládají pouze tehdy, pokud splňují filtry aktivního profilu.
6. Program skončí po dosažení limitu nebo vyčerpání fronty.

### 4.2 Stavový popis

- inicializace front a vláken
- běžící worker vlákna
- čekání na dokončení fronty
- poslání sentinelů
- ukončení loggeru
- zápis výsledků

---

## 5. Rozhraní, protokoly a knihovny

### 5.1 Knihovny třetích stran

- **requests** – HTTP klient
- **beautifulsoup4** – HTML parsování
- **tqdm** – progress bar

### 5.2 Standardní knihovny

- threading
- queue
- time
- urllib.parse
- pathlib
- configparser
- dataclasses
- json

### 5.3 Právní aspekty

Projekt je školní práce.  
Uživatel musí respektovat legislativu a robots.txt.

---

## 6. Konfigurace

Ukázka `config.ini`:

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
profiles = contacts, seo, content
profile = seo
save_html = false
```

### Hlavní volby

- **profile** – aktivní režim těžby
- **profiles** – seznam dostupných režimů
- **save_html** – zda ukládat HTML na disk
- ostatní volby odpovídají staré verzi projektu

---

## 7. Instalace a spuštění

### 7.1 Předpoklady

- Python 3.x
- přístup k instalaci balíčků
- možnost spouštět příkazy v terminálu

### 7.2 Instalace závislostí

```bash
pip install -r requirements.txt
```

### 7.3 Spuštění programu

Správné spuštění modulu:

```bash
python -m src.main
```

Spuštění s vlastním konfiguračním souborem:

```bash
python -m src.main muj_config.ini
```

---

## 8. Struktura projektu

```
project/
├── config.ini
├── requirements.txt
├── README.md
├── doc/
│   └── documentation.md
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

## 9. Testování

Projekt obsahuje sadu jednotkových testů:

- testy extractorů
- test textové extrakce
- test filtrování dat
- test prázdných výsledků
- test neočekávaných HTML stavů

Testy se spouští:

```bash
python -m unittest discover -s tests
```

Součástí projektu je i **uživatelské testování** – dotazník a protokol.

---

## 10. Praktické využití

Typické scénáře využití:

- sběr kontaktů pro firmy nebo seznamy
- SEO audit konkurenčních webů
- extrakce textů pro analýzu, učení nebo NLP
- automatizace sběru veřejných informací
- příprava datasetů

Vícevláknové zpracování zajišťuje vyšší rychlost a volba profilu dává uživateli přesnou kontrolu nad tím, jaká data chce těžit.

---

## 11. Ukončení běhu

Crawler se ukončí:

- vyčerpáním fronty
- dosažením `max_pages`
- nebo ruční volbou v menu

Logger doběhne až po zapsání všech zpráv.

---

