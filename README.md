# News Scraper

Ferramenta para coleta automatizada de notícias financeiras de **19 fontes globais** (PT e EN), com suporte a scraping via browser, extração de metadados e armazenamento em dataset Parquet particionado.

## Fontes Suportadas

**Português (4 fontes)**:
- InfoMoney, MoneyTimes, Valor Econômico, E-Investidor (Estadão)

**Inglês (15 fontes)**:
- Yahoo Finance, Bloomberg, Reuters, CNBC, MarketWatch
- Business Insider, Investing.com, Forbes, Investopedia
- Financial Times, WSJ, Economist, Barron's, Seeking Alpha
- Bloomberg LatAm

## Requisitos

- Python **3.11+**
- Chrome/Chromium (para scraping com browser)

## Instalação

```bash
git clone https://github.com/seu-usuario/news-scraper.git
cd news-scraper
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -e .
```

## Uso Básico

### 1. Coletar notícias de uma fonte específica

**InfoMoney (últimos artigos)**:

```python
from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.sources.pt import InfoMoneyScraper

config = BrowserConfig(headless=True)
with ProfessionalScraper(config) as browser:
    scraper = InfoMoneyScraper(browser)
    urls = scraper.get_latest_articles(category="mercados", limit=20)
    print(f"Coletadas {len(urls)} URLs")
```

**Categorias disponíveis**: `mercados`, `economia`, `politica`, `negocios`

**Yahoo Finance (notícias dos EUA)**:

```python
from news_scraper.sources.en import YahooFinanceUSScraper

with ProfessionalScraper(config) as browser:
    scraper = YahooFinanceUSScraper(browser)
    urls = scraper.get_latest_articles(limit=20)
```

### 2. Extrair conteúdo completo de URLs

```python
from news_scraper.extract import extract_article_metadata

url = "https://www.infomoney.com.br/mercados/exemplo/"
with ProfessionalScraper(config) as browser:
    metadata = extract_article_metadata(url, browser.driver)
    print(f"Título: {metadata['title']}")
    print(f"Texto: {metadata['text'][:200]}...")
```

### 3. Salvar em dataset Parquet (análise temporal)

```python
from news_scraper.dataset import write_to_dataset

articles = []
with ProfessionalScraper(config) as browser:
    scraper = InfoMoneyScraper(browser)
    urls = scraper.get_latest_articles(limit=10)
    
    for url in urls:
        metadata = extract_article_metadata(url, browser.driver)
        articles.append(metadata)

# Salva particionado por ano/mês/dia/fonte
write_to_dataset(articles, "data/processed/articles")
```

### 4. Consultar dados com SQL (DuckDB)

```bash
# Ver estatísticas gerais
python -m news_scraper.query stats --dataset-dir data/processed/articles

# Consulta SQL customizada
python -m news_scraper.query sql \
  --dataset-dir data/processed/articles \
  --sql "SELECT source, COUNT(*) as total FROM articles GROUP BY source"
```

Ou direto em Python:

```python
import duckdb

con = duckdb.connect()
df = con.execute("""
  SELECT source, COUNT(*) as total, AVG(LENGTH(text)) as avg_chars
  FROM read_parquet('data/processed/articles/**/*.parquet')
  WHERE date_published >= '2026-01-01'
  GROUP BY source
  ORDER BY total DESC
""").df()
print(df)
```

## Exemplos Avançados

### Coletar de múltiplas fontes

```python
from news_scraper.sources.pt import InfoMoneyScraper, MoneyTimesScraper, ValorScraper
from news_scraper.sources.en import ReutersScraper, CNBCScraper

sources = [
    ("InfoMoney", InfoMoneyScraper, "mercados"),
    ("MoneyTimes", MoneyTimesScraper, "mercado"),
    ("Valor", ValorScraper, "financas"),
    ("Reuters", ReutersScraper, "markets"),
    ("CNBC", CNBCScraper, "markets"),
]

all_urls = []
with ProfessionalScraper(config) as browser:
    for name, ScraperClass, category in sources:
        scraper = ScraperClass(browser)
        urls = scraper.get_latest_articles(category=category, limit=10)
        print(f"{name}: {len(urls)} URLs")
        all_urls.extend(urls)

print(f"Total: {len(all_urls)} URLs")
```

### Filtrar por período (coleta histórica)

```python
from datetime import datetime, timedelta

# Gerar URLs por padrão de data
from news_scraper.historical import generate_urls_by_pattern

start = datetime(2025, 1, 1)
end = datetime(2025, 12, 31)
pattern = "https://exemplo.com/arquivo/{YYYY}/{MM}/{DD}/"

urls = generate_urls_by_pattern(pattern, start, end)
with open("urls_2025.txt", "w") as f:
    f.write("\n".join(urls))
```

### Exportar para análise

```python
import duckdb

con = duckdb.connect()
con.execute("""
  COPY (
    SELECT title, text, date_published, source
    FROM read_parquet('data/processed/articles/**/*.parquet')
    WHERE source = 'infomoney.com.br'
      AND date_published >= '2026-01-01'
  ) TO 'export_infomoney.csv' (HEADER, DELIMITER ',')
""")
```

## Estrutura do Projeto

```
news-scraper/
├── src/news_scraper/
│   ├── sources/           # Scrapers especializados por fonte
│   │   ├── pt/           # InfoMoney, MoneyTimes, Valor, E-Investidor
│   │   ├── en/           # YahooFinance, Bloomberg, Reuters, etc.
│   │   └── base_scraper.py  # Classe base com retry, métricas, validação
│   ├── browser.py        # Automação com Selenium (ProfessionalScraper)
│   ├── extract.py        # Extração de metadados (título, texto, data, autor)
│   ├── dataset.py        # Escrita Parquet particionada
│   ├── query.py          # Consultas SQL (DuckDB)
│   └── historical.py     # Coleta de períodos passados (sitemaps, padrões)
├── tests/                # 200+ testes (unit, integration, benchmarks)
├── data/
│   ├── raw/             # URLs coletadas
│   └── processed/       # Dataset Parquet (year/month/day/source)
└── docs/                # Documentação técnica
```

## Categorias por Fonte

| Fonte | Categorias Disponíveis |
|-------|----------------------|
| **InfoMoney** | `mercados`, `economia`, `politica`, `negocios` |
| **MoneyTimes** | `mercado`, `investimentos`, `economia` |
| **Valor** | `financas`, `empresas`, `mercados`, `mundo`, `politica` |
| **E-Investidor** | `mercados`, `investimentos`, `fundos-imobiliarios`, `cripto` |
| **Yahoo Finance** | Sem categorias (feed principal) |
| **Bloomberg** | `markets`, `economics`, `technology`, `politics` |
| **Reuters** | `markets`, `business`, `world`, `technology` |
| **CNBC** | `markets`, `investing`, `economy` |
| **MarketWatch** | `markets`, `investing`, `personal-finance` |
| **Outros** | Consulte a documentação de cada scraper |

## Configuração de Métricas

Cada scraper possui:
- **MIN_SUCCESS_RATE**: Taxa mínima de sucesso (ex: 0.6 = 60%)
- **HAS_PAYWALL**: Indica se tem paywall (`True`, `False`, `"partial"`)
- **Retry automático**: 3 tentativas com backoff exponencial
- **Coleta de métricas**: Tempo, taxa de sucesso, erros

Exemplo de uso:

```python
from news_scraper.sources.base_scraper import MetricsCollector

# Após executar scrapers, ver métricas agregadas
collector = MetricsCollector()
stats = collector.get_statistics()
print(f"Taxa média de sucesso: {stats['average_success_rate']:.1%}")
print(f"Total de erros: {stats['total_errors']}")
```

## Limitações e Considerações

- **Paywalls**: Fontes com paywall (WSJ, FT, Economist, Barron's) têm taxa de sucesso baixa (20-30%)
- **Anti-scraping**: Alguns sites podem bloquear após muitas requisições
- **Extração**: Heurística, pode falhar em layouts dinâmicos ou não-padrão
- **Performance**: Browser scraping é lento (2-5s por página)

**Recomendações**:
- Use `headless=True` para melhor performance
- Adicione delays entre requisições (`time.sleep(2)`)
- Para grandes volumes, considere proxies rotativos
- Prefira RSS quando disponível

## Scripts de Demonstração

```bash
# InfoMoney completo (coleta + análise)
python scripts/demo_infomoney.py

# Investigar estrutura de um site novo
python scripts/investigate_site.py https://exemplo.com.br
```

## Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Testes rápidos (metadados e estrutura)
pytest tests/test_global_sources.py -v

# Benchmarks de performance
pytest tests/test_scraper_benchmarks.py -v

# Teste de um scraper específico
pytest tests/test_infomoney_scraper.py -v
```

## Documentação Adicional

- **[docs/HISTORICAL.md](docs/HISTORICAL.md)** - Coleta de notícias históricas (sitemaps, padrões de URL)
- **[docs/TEST_COVERAGE.md](docs/TEST_COVERAGE.md)** - Cobertura de testes e benchmarks
- **[docs/SOURCES_ORGANIZATION.md](docs/SOURCES_ORGANIZATION.md)** - Organização dos scrapers por idioma
- **[EXAMPLE_WORKFLOW.md](EXAMPLE_WORKFLOW.md)** - Workflow completo para análise de dados

## Licença

MIT License - uso acadêmico e pessoal. Respeite os termos de uso dos sites raspados.
