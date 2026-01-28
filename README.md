# News Scraper (acadêmico)

Projeto em Python para **extrair notícias a partir de URLs e/ou RSS** e salvar em **JSONL/CSV** ou em um **dataset Parquet particionado** (ideal para análise de sentimento e séries temporais via DuckDB/Pandas).

> Finalidade acadêmica: use com responsabilidade, respeitando `robots.txt`, termos de uso e limites de requisição.

## Recursos

- 🔍 Scraping de notícias via URLs ou RSS
- 📊 Dataset Parquet particionado por data e fonte (otimizado para análise)
- 🗄️ Consultas SQL direto no dataset (DuckDB)
- 📋 Gerenciamento de fontes via CSV (fácil de manter)
- 📈 Estatísticas rápidas do dataset
- ⏱️ Timestamps `scraped_at` para rastreabilidade temporal

## Requisitos

- Python **3.11+**

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

## Uso rápido

### Exemplo prático: InfoMoney

**Passo 1: Extrair URLs com browser scraping**

```python
# Criar script para extrair URLs de artigos
from news_scraper.browser import BrowserConfig, ProfessionalScraper

config = BrowserConfig(headless=True)
with ProfessionalScraper(config) as scraper:
    scraper.get_page('https://www.infomoney.com.br/', wait_time=3)
    scraper.scroll_and_load(scroll_pause=1.5, max_scrolls=3)
    
    all_links = scraper.driver.find_elements('css selector', 'a')
    
    article_urls = []
    for link in all_links:
        href = link.get_attribute('href')
        if href and '/mercados/' in href and len(href) > 60:
            article_urls.append(href)
    
    article_urls = sorted(set(article_urls))[:20]
    
    with open('data/raw/infomoney_urls.txt', 'w') as f:
        f.write('\n'.join(article_urls))
    
    print(f"✓ {len(article_urls)} URLs salvas")
```

**Passo 2: Scrape os artigos para dataset Parquet**

```bash
news-scraper scrape \
  --input data/raw/infomoney_urls.txt \
  --dataset-dir data/processed/articles \
  --delay 2.0
```

**Passo 3: Consultar os dados**

```bash
# Ver estatísticas
news-scraper stats --dataset-dir data/processed/articles

# Consultar com SQL
news-scraper query --dataset-dir data/processed/articles \
  --sql "SELECT title, LENGTH(text) as chars FROM articles LIMIT 5"

# Exportar para análise de sentimento
news-scraper query --dataset-dir data/processed/articles \
  --sql "SELECT title, text FROM articles" \
  --format csv > infomoney_export.csv
```

Ou use o script de demonstração completo:

```bash
python scripts/demo_infomoney.py
```

### 1) Extrair a partir de uma lista de URLs

```bash
news-scraper scrape --input urls.txt --out outputs/noticias.jsonl
```

Para dataset analítico (Parquet particionado por data/fonte):

```bash
news-scraper scrape --input urls.txt --dataset-dir data/processed/articles
```

Formato CSV:

```bash
news-scraper scrape --input urls.txt --out outputs/noticias.csv --format csv
```

### 2) Coletar links a partir de RSS (e opcionalmente já raspar)

Apenas listar links:

```bash
news-scraper rss --feed https://exemplo.com/rss.xml --out outputs/links.txt
```

Ou carregar a lista de feeds a partir de um CSV (mais fácil de manter):

```bash
news-scraper rss --sources-csv configs/sources.csv --out outputs/links.txt
```

Listar e já raspar os artigos:

```bash
news-scraper rss --feed https://exemplo.com/rss.xml --scrape --out outputs/noticias.jsonl
```

Raspar e gravar direto no dataset Parquet:

```bash
news-scraper rss --sources-csv configs/sources.csv --scrape --dataset-dir data/processed/articles
```

### 3) Gerenciar fontes (CSV)

Listar fontes:

```bash
news-scraper sources list
```

Adicionar uma fonte:

```bash
news-scraper sources add --id folha --name "Folha de S.Paulo" --type rss \
  --url "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml" --tags "brasil;geral"
```

Desabilitar/habilitar:

```bash
newWorkflow recomendado (análise de sentimento por período)

1. **Configure fontes** em `configs/sources.csv` (enabled, RSS, tags)
2. **Colete artigos históricos** via scraping:
   ```bash
   news-scraper scrape --input urls_historico.txt --dataset-dir data/processed/articles
   ```
3. **Monitore feeds RSS** periodicamente (cron/agendamento):
   ```bash
   news-scraper rss --sources-csv configs/sources.csv --scrape --dataset-dir data/processed/articles
   ```
4. **Consulte por período** e exporte para análise:
   ```bash
   news-scraper query --dataset-dir data/processed/articles \
     --sql "SELECT * FROM articles WHERE date_published BETWEEN '2020-01-01' AND '2020-01-31'" \
     --format json > janeiro_2020.jsonl
   ```
5. **Análise de sentimento** (fora deste projeto): use bibliotecas como `transformers`, `textblob`, ou APIs especializadas sobre o JSONL exportado.

## Consultar com DuckDB diretamente (Python/SQL)

```python
import duckdb
con = duckdb.connect()
df = con.execute("""
  SELECT source, count(*) as total
  FROM read_parquet('data/processed/articles/**/*.parquet')
  WHERE date_published >= '2020-01-01' AND date_published < '2020-02-01'
  GROUP BY source
  ORDER BY total DESC
""").df()
print(df)taset-dir data/processed/articles \
  --sql "SELECT source, count(*) as total FROM articles WHERE date_published >= '2020-01-01' AND date_published < '2020-02-01' GROUP BY source ORDER BY total DESC"
```

Exportar para CSV:

```bash
news-scraper query --dataset-dir data/processed/articles \
  --sql "SELECT url, title, date_published FROM articles WHERE source = 'example.com' LIMIT 10" \
  --format csv > resultados.csv
```

### 5) Estatísticas rápidas

```bash
news-scraper stats --dataset-dir data/processed/articles
```

Mostra: total de artigos, top fontes, período coberto, artigos com erro.

## Boas práticas (acadêmicas)

- Preferir RSS quando existir.
- Use `--respect-robots` (padrão: ligado) e aumente `--delay` se necessário.
- Identifique-se com `--user-agent`.
- Evite raspar paywalls e conteúdos que violem termos do site.

## Estrutura

- `src/news_scraper/cli.py`: CLI (`news-scraper`)
- `src/news_scraper/scrape.py`: pipeline de scraping
- `src/news_scraper/extract.py`: extração do conteúdo do HTML
- `src/news_scraper/polite.py`: throttling + robots
- `src/news_scraper/rss.py`: coleta de links via RSS
- `src/news_scraper/io.py`: exportação JSONL/CSV
- `src/news_scraper/dataset.py`: escrita Parquet particionada (DuckDB-friendly)
- `src/news_scraper/sources.py`: leitura de fontes via CSV

## Consultar com DuckDB (exemplo)

Com o dataset em `data/processed/articles`, você pode consultar assim:

```sql
SELECT source, count(*)
FROM read_parquet('data/processed/articles/**/*.parquet')
WHERE date_published >= '2020-01-01' AND date_published < '2020-02-01'
GROUP BY source
ORDER BY count(*) DESC;
```

## Limitações

Extração de conteúdo é heurística e varia por site. Alguns sites usam scripts, paywalls ou bloqueios; nesses casos, a extração pode falhar ou vir incompleta.

## Documentação adicional

- **[docs/HISTORICAL.md](docs/HISTORICAL.md)** - 🔥 **Como coletar notícias de períodos passados** (sitemaps, padrões de URL, arquivos)
- [EXAMPLE_WORKFLOW.md](EXAMPLE_WORKFLOW.md) - Workflow completo para análise de sentimento
- [docs/DEDUPLICATION.md](docs/DEDUPLICATION.md) - Estratégias de deduplicação
- [docs/TIPS.md](docs/TIPS.md) - Dicas de escalabilidade, ética e troubleshooting
- [data/README.md](data/README.md) - Estrutura de dados recomendada
- [configs/README.md](configs/README.md) - Documentação do sources.csv

## Comandos rápidos (cheat sheet)

``=== Coleta histórica (períodos passados) ===

# Gerar URLs por padrão de data
news-scraper historical generate \
  --pattern "https://site.com/arquivo/{YYYY}/{MM}/{DD}/" \
  --start 2020-01-01 --end 2020-12-31 \
  --out urls_2020.txt

# Extrair de sitemap
news-scraper historical sitemap \
  --url https://example.com/sitemap.xml \
  --filter "/2020/" --out urls_2020.txt

# Scrape das URLs históricas
news-scraper scrape --input urls_2020.txt --dataset-dir data/processed/articles

# === Coleta contínua (RSS) ===

# Coletar de RSS configurado
news-scraper rss --sources-csv configs/sources.csv --scrape --dataset-dir data/processed/articles

# === Análise ===
news-scraper rss --sources-csv configs/sources.csv --scrape --dataset-dir data/processed/articles

# Ver estatísticas
news-scraper stats --dataset-dir data/processed/articles

# Consultar período específico
news-scraper query --dataset-dir data/processed/articles \
  --sql "SELECT * FROM articles WHERE date_published BETWEEN '2020-01-01' AND '2020-01-31'" \
  --format json > janeiro.jsonl

# Adicionar fonte
news-scraper sources add --id g1 --name "G1" --type rss --url "https://g1.globo.com/rss/g1/"

# Listar fontes
news-scraper sources list
```
