# Dicas e boas práticas

## Escalando a coleta

### Múltiplos workers (paralelo)

Para coletar de muitas fontes simultaneamente:

```bash
# Separe fontes em múltiplos CSVs ou use tags
news-scraper rss --sources-csv configs/sources_brasil.csv --scrape --dataset-dir data/processed/articles &
news-scraper rss --sources-csv configs/sources_internacional.csv --scrape --dataset-dir data/processed/articles &
wait
```

Ou use ferramentas como GNU Parallel:

```bash
cat urls_lote1.txt | parallel -j 4 \
  "news-scraper scrape --url {} --dataset-dir data/processed/articles"
```

### Coleta incremental (cron)

Para monitorar feeds diariamente:

```bash
# crontab -e
0 */6 * * * cd /path/to/news-scraper && .venv/bin/news-scraper rss --sources-csv configs/sources.csv --scrape --dataset-dir data/processed/articles --limit 50 >> logs/scraper.log 2>&1
```

## Otimizando consultas DuckDB

### Filtros no WHERE

DuckDB usa "predicate pushdown" — filtre por partições quando possível:

```sql
-- Rápido (usa partições year/month/day)
SELECT * FROM articles WHERE date_published >= '2020-01-01' AND date_published < '2020-02-01'

-- Mais lento (full scan)
SELECT * FROM articles WHERE title LIKE '%eleições%'
```

### Índices e agregações

Para análises repetidas, considere materializar views:

```python
import duckdb
con = duckdb.connect('cache.duckdb')

# Cria tabela local otimizada
con.execute("""
  CREATE TABLE articles_cache AS 
  SELECT * FROM read_parquet('data/processed/articles/**/*.parquet')
""")

# Queries subsequentes são muito mais rápidas
df = con.execute("SELECT * FROM articles_cache WHERE source = 'g1'").df()
```

## Privacidade e ética

- **Respeite robots.txt**: o scraper já faz isso por padrão.
- **Rate limiting**: use `--delay` adequado (padrão: 1s).
- **Termos de uso**: alguns sites proíbem scraping — sempre verifique.
- **Paywall**: evite burlar paywalls; use fontes que disponibilizam conteúdo aberto.
- **Dados pessoais**: notícias podem mencionar pessoas; anonimize se for publicar análises.

## Reprodutibilidade

Para trabalhos acadêmicos:

1. **Versione o `sources.csv`** (git).
2. **Documente timestamps**: use `scraped_at` para saber quando coletou.
3. **Congele datasets**: após coletar, faça backup antes de análises (`cp -r data/processed/articles data/processed/articles_v1`).
4. **Registre versões de bibliotecas**: `pip freeze > requirements-lock.txt`.

## Análise de sentimento: dicas

### Pré-processamento

Antes de aplicar modelos:

```python
import re

def clean_text(text):
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove excesso de espaços
    text = re.sub(r'\s+', ' ', text).strip()
    return text

df['text_clean'] = df['text'].apply(clean_text)
```

### Modelos recomendados (português)

- **BERTimbau**: `neuralmind/bert-base-portuguese-cased`
- **Multilingual**: `nlptown/bert-base-multilingual-uncased-sentiment`
- **APIs**: Azure Text Analytics, Google Cloud Natural Language

### Agregação temporal

Agrupe por dia/semana para comparar com eventos:

```python
df['date'] = pd.to_datetime(df['date_published']).dt.date
daily_sentiment = df.groupby('date')['sentiment_score'].mean()

# Plotar
daily_sentiment.plot(title='Sentimento médio ao longo do tempo')
```

## Troubleshooting

### Erro: `Permission denied by robots.txt`

Fonte bloqueou o scraping. Opções:
- Respeite a decisão (recomendado).
- Use `--no-respect-robots` (apenas se tiver permissão explícita).
- Busque fonte alternativa (RSS, API oficial).

### Extração de texto vazia

Alguns sites usam JavaScript pesado. Soluções:
- Use Selenium/Playwright (fora do escopo deste projeto).
- Preferir RSS (já vem com texto resumido).
- Testar manualmente: `curl <url>` e verificar se HTML tem conteúdo.

### Dataset muito grande

DuckDB lida bem com gigabytes. Se ficar lento:
- Particione melhor (por mês + fonte).
- Use `LIMIT` em queries exploratórias.
- Considere Spark/Dask para terabytes.
