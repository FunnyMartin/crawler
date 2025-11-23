# Multithreaded Web Crawler – dokumentace

Autor: Martin Šilar  
Škola: SPŠE Ječná  
Ročník: 4.  
Předmět: PV – školní projekt (souběžné programování)  
Kontakt: silar@spsejecna.cz  
Datum vypracování: 23. 11. 2025


## 1. Název a účel projektu

**Název projektu:** Multithreaded Web Crawler

**Stručný popis:**  
Projekt je vícevláknový webový crawler v jazyce Python. Aplikace paralelně prochází web v rámci jedné domény, stahuje HTML stránky, ukládá je na disk a zapisuje průběh do logu. Crawler využívá několik pracovních vláken, která si z fronty odebírají URL ke zpracování. Další vlákno slouží jako logger a sériově zapisuje logovací zprávy do souboru, aby se předešlo konfliktům při zápisu.

**Účel projektu:**  
Prokázat praktické použití paralelního a souběžného zpracování v reálné úloze, ukázat použití klasického vzoru producer–consumer, řešit synchronizaci nad sdílenými zdroji a vytvořit konfigurovatelný nástroj, který dokáže stáhnout omezenou část webu v rámci jedné domény.

Jedná se o školní projekt, nikoliv nástroj určený pro masivní indexování internetu.


## 2. Požadavky uživatele

### 2.1 Funkční požadavky

1. Uživatel nastaví počáteční URL (start_url), ze které crawler začíná procházet web.
2. Crawler smí procházet pouze odkazy v rámci jedné domény (allowed_domain).
3. Program musí být vícevláknový, několik worker vláken stahuje stránky paralelně.
4. Každá stažená stránka se uloží do adresáře output_dir jako samostatný HTML soubor.
5. Aplikace vede seznam již navštívených URL (visited), aby se jednotlivé stránky nestahovaly opakovaně.
6. Počet stažených stránek omezuje parametr max_pages.
7. Průběh běhu je zapisován do logovacího souboru (log_file) přes jedno samostatné logovací vlákno.
8. Aplikace je spustitelná z příkazové řádky bez použití IDE.

### 2.2 Nefunkční požadavky

1. **Výkon**  
   Vícevláknové zpracování musí být efektivnější než sekvenční stahování, pokud je k dispozici dostatek odkazů.

2. **Omezení zdrojů a bezpečnost**  
   Crawler nesmí pracovat mimo povolenou doménu.  
   Fronta úloh (queue_maxsize) je omezena, aby nedošlo k nadměrnému využití paměti.  
   Každý HTTP požadavek má vlastní časový limit.

3. **Robustnost**  
   Chyby při stahování (například timeouty nebo HTTP chyby 4xx/5xx) nesmějí ukončit běh programu.  
   Chyby se pouze zapisují do logu.

4. **Konfigurovatelnost**  
   Všechna důležitá nastavení jsou uložena v souboru config.ini. Uživatel nemusí měnit zdrojový kód.

5. **Čitelnost a údržba**  
   Kód je rozdělen do modulů main.py, config.py a crawler.py.  
   Konfigurace je reprezentována datovou třídou CrawlerConfig.

6. **Přenositelnost**  
   Program musí být spustitelný na školních počítačích s Pythonem 3.x a možností instalace balíčků z requirements.txt.


### Respektování robots.txt a omezení crawlingu

Crawler podporuje pravidla definovaná v souboru robots.txt v kořenové části domény.

Při startu aplikace se soubor robots.txt stáhne a zpracuje. Podporované direktivy:

**Disallow**  
URL jejichž cesta začíná některou z direktiv Disallow, nejsou vloženy do fronty a nejsou stahovány.

**Crawl-delay**  
Pokud robots.txt obsahuje direktivu Crawl-delay, crawler čeká uvedený počet sekund mezi dvěma HTTP požadavky. Tím se snižuje zátěž serveru a minimalizuje riziko blokování.

**Význam**  
Respektování robots.txt zajišťuje etické chování crawleru, snižuje riziko zablokování serverem a odpovídá běžným standardům provozu crawlerů. Servery s dlouhým Crawl-delay nebo se skrytými odkazy mohou crawler omezit v počtu dostupných URL, což je očekávané a v souladu s pravidly serveru.


### 2.3 Use Case (slovní popis)

**Use Case: Stažení části webu**

- Aktér: student
- Předpoklad: instalovaný Python, nainstalované závislosti a vyplněný config.ini.
- Postup:
    1. Uživatel nastaví start_url a allowed_domain.
    2. Spustí příkaz python src/main.py.
    3. Crawler vytvoří worker vlákna a začne paralelně stahovat stránky.
    4. Stažené stránky jsou ukládány do adresáře data.
    5. Logovací vlákno průběžně zapisuje logy.
    6. Po dosažení limitu max_pages nebo po vyčerpání URL crawler automaticky skončí.
- Výsledek: sada HTML souborů ve složce data a záznam logů v logs/crawler.log.


## 3. Architektura aplikace

### 3.1 Moduly a soubory

**src/main.py**  
Vstupní bod aplikace.  
Načítá konfiguraci a spouští crawler.

**src/webcrawler/config.py**  
Obsahuje datovou třídu CrawlerConfig.  
Zajišťuje načtení a interpretaci souboru config.ini.

**src/webcrawler/crawler.py**  
Obsahuje implementaci třídy WebCrawler.  
Řeší fronty, vlákna, synchronizaci, stahování a ukládání HTML.

### 3.2 Architektura – textové schéma

- main.py načte konfiguraci, vytvoří instanci crawleru a zavolá run().
- WebCrawler.run() vytvoří logger vlákno a pracovní vlákna.
- Startovní URL je vložena do fronty.
- Workery paralelně stahují stránky, extrahují odkazy a přidávají je do fronty.
- Po vyčerpání úloh se pošlou sentinely pro ukončení workerů.
- Logger ukončí činnost po zpracování všech zpráv.


## 4. Popis běhu aplikace

### 4.1 Typický běh

1. Načtení konfigurace a vytvoření instance WebCrawler.
2. Spuštění logger vlákna.
3. Spuštění worker vláken.
4. Vložení start_url do fronty.
5. Workery stahují HTML, ukládají data a přidávají nové URL.
6. main thread čeká na vyprázdnění fronty.
7. Po dokončení práci workerů ukončí sentinely.
8. Logger se ukončí po zpracování všech zpráv.
9. Program vypíše informaci o dokončení.

### 4.2 Stavy

Inicializace, běh, čekání na frontu, ukončování vláken, konec aplikace.


## 5. Rozhraní, protokoly a knihovny

### 5.1 Síťová komunikace

Aplikace používá HTTP/HTTPS požadavky pomocí knihovny requests.

### 5.2 Knihovny třetích stran

requests (Apache 2.0)  
beautifulsoup4 (MIT)

### 5.3 Standardní knihovny Pythonu

threading, queue, time, urllib.parse, pathlib, configparser, dataclasses

### 5.4 Právní aspekty

Projekt je školní práce.  
Použité knihovny jsou použity v rámci svých licencí.  
Crawler by měl být používán pouze na stránkách, které crawling povolují.


## 6. Konfigurace programu

Konfigurace je v souboru config.ini:

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

### Význam voleb

start_url: počáteční URL  
allowed_domain: doména, ve které se crawler pohybuje  
max_workers: počet worker vláken  
max_pages: maximální počet stahovaných stránek  
queue_maxsize: kapacita fronty  
request_timeout: timeout HTTP požadavku  
user_agent: identifikace crawleru  
output_dir: cílový adresář pro HTML  
log_file: cesta k logovacímu souboru


## 7. Instalace a spuštění

### 7.1 Předpoklady

nainstalovaný Python 3.x  
přístup k internetu  
možnost instalace balíčků z requirements.txt

### 7.2 Instalace závislostí

```
pip install -r requirements.txt
```

### 7.3 Spuštění

```
python src/main.py
```

nebo

```
python src/main.py muj_config.ini
```


### 7.4 Struktura projektu

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

### 7.5 Doporučený postup

Upravit config.ini, nainstalovat závislosti, spustit aplikaci a ověřit výstupy.

### 7.6 Ukončení

Crawler se ukončí po dosažení limitu, po vyčerpání URL nebo ručním ukončením. Logger skončí po dopsání všech zpráv.
