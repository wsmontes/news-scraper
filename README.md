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

## Uso Básico (CLI)

### 1. Coletar notícias de uma fonte específica

**InfoMoney (últimos 20 artigos)**:

```bash
python -m news_scraper collect --source infomoney --limit 20 --dataset-dir data/processed/articles
```

**Valor categoria mercados**:

```bash
python -m news_scraper collect --source valor --category mercados --limit 15 --dataset-dir data/processed/articles
```

**Múltiplas fontes de uma vez**:

```bash
python -m news_scraper collect --source infomoney --source moneytimes --source valor --limit 10 --dataset-dir data/processed/articles
```

**Categorias disponíveis por fonte**:
- **InfoMoney**: `mercados`, `economia`, `politica`, `negocios`
- **MoneyTimes**: `mercado`, `investimentos`, `negocios`
- **Valor**: `financas`, `empresas`, `investimentos`
- **E-Investidor**: `mercados`, `acoes`

### 2. Extrair conteúdo de URLs específicas

```bash
# Arquivo com URLs (1 por linha)
python -m news_scraper scrape --input urls.txt --out artigos.jsonl

# URLs diretas
python -m news_scraper scrape \
  --url "https://www.infomoney.com.br/mercados/exemplo/" \
  --url "https://www.valor.com.br/financas/exemplo/" \
  --out artigos.jsonl

# Salvar direto no dataset Parquet
python -m news_scraper scrape --input urls.txt --dataset-dir data/processed/articles
```

### 3. Consultar dados com SQL (DuckDB)

```bash
# Ver estatísticas gerais
python -m news_scraper stats --dataset-dir data/processed/articles

# Consulta SQL customizada (formato tabela)
python -m news_scraper query \
  --dataset-dir data/processed/articles \
  --sql "SELECT source, COUNT(*) as total FROM articles GROUP BY source ORDER BY total DESC"

# Exportar para CSV
python -m news_scraper query \
  --dataset-dir data/processed/articles \
  --sql "SELECT * FROM articles WHERE source = 'infomoney.com.br' LIMIT 100" \
  --format csv > export.csv

# Exportar para JSON
python -m news_scraper query \
  --dataset-dir data/processed/articles \
  --sql "SELECT title, date_published FROM articles WHERE date_published >= '2026-01-01'" \
  --format json > artigos_2026.json
```

### 4. Coletar de feeds RSS

```bash
# RSS específico
python -m news_scraper rss --feed "https://exemplo.com/rss" --out links.txt

# RSS + scraping automático
python -m news_scraper rss \
  --feed "https://exemplo.com/rss" \
  --scrape \
  --dataset-dir data/processed/articles \
  --limit 50

# Usar sources.csv (apenas feeds enabled=1)
python -m news_scraper rss \
  --sources-csv configs/sources.csv \
  --scrape \
  --dataset-dir data/processed/articles
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

## Comandos CLI Avançados

### Gerenciar fontes (sources.csv)

```bash
# Listar todas as fontes
python -m news_scraper sources list

# Adicionar nova fonte
python -m news_scraper sources add \
  --id "minhafonte" \
  --name "Minha Fonte" \
  --type rss \
  --url "https://minhafonte.com/rss"

# Habilitar/desabilitar fonte
python -m news_scraper sources enable minhafonte
python -m news_scraper sources disable minhafonte
```

### Coleta histórica

```bash
# Gerar URLs por padrão de data
python -m news_scraper historical generate \
  --pattern "https://exemplo.com/arquivo/{YYYY}/{MM}/{DD}/" \
  --start 2025-01-01 \
  --end 2025-12-31 \
  --out urls_2025.txt

# Extrair URLs de página de arquivo
python -m news_scraper historical archive \
  --url "https://exemplo.com/arquivo/2025/" \
  --out urls_arquivo.txt
```

### Scraping com browser (JavaScript, paywalls)

```bash
# Modo browser completo (Selenium + Chrome)
python -m news_scraper browser \
  --url "https://site-com-javascript.com/artigo" \
  --out artigo.json

# Com proxy e modo headless desabilitado
python -m news_scraper browser \
  --url "https://site-protegido.com/" \
  --use-proxy \
  --no-headless
```

### Filtros e limites

```bash
# Filtrar por data (após coleta)
python -m news_scraper collect \
  --source infomoney \
  --start-date 2026-01-01 \
  --end-date 2026-01-31 \
  --dataset-dir data/processed/articles

# Apenas coletar URLs (sem scraping)
python -m news_scraper collect \
  --source valor \
  --category mercados \
  --skip-scrape \
  --urls-out valor_urls.txt

# Modo verboso (debug)
python -m news_scraper collect \
  --source moneytimes \
  --verbose \
  --limit 5
```

## API Python (Uso Programático)

Para integração em projetos Python:

### Coletar de múltiplas fontes

```python
from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.sources.pt import InfoMoneyScraper, ValorScraper
from news_scraper.sources.en import ReutersScraper

config = BrowserConfig(headless=True)
sources = [
    ("InfoMoney", InfoMoneyScraper, "mercados"),
    ("Valor", ValorScraper, "financas"),
    ("Reuters", ReutersScraper, "markets"),
]

all_urls = []
with ProfessionalScraper(config) as browser:
    for name, ScraperClass, category in sources:
        scraper = ScraperClass(browser)
        urls = scraper.get_latest_articles(category=category, limit=10)
        print(f"{name}: {len(urls)} URLs")
        all_urls.extend(urls)
```

### Análise com DuckDB (Python)

```python
import duckdb

con = duckdb.connect()
df = con.execute("""
  SELECT source, COUNT(*) as total, AVG(LENGTH(text)) as avg_chars
  FROM read_parquet('data/processed/articles/**/*.parquet')
  WHERE date_published >= '2026-01-01'
  GROUP BY source ORDER BY total DESC
""").df()

print(df)
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
