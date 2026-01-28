# Deduplicação de artigos

## Contexto

Ao coletar notícias ao longo do tempo (RSS diário, re-scraping, etc.), é comum ter duplicatas por URL. O dataset Parquet particionado **permite** duplicatas por design (cada scraping gera novos arquivos).

## Estratégias

### 1. Deduplicação na consulta (SQL)

Use `DISTINCT ON` ou `ROW_NUMBER()` para pegar apenas a versão mais recente de cada URL:

```sql
SELECT DISTINCT ON (url) *
FROM read_parquet('data/processed/articles/**/*.parquet')
ORDER BY url, scraped_at DESC
```

Ou com DuckDB via Python:

```python
import duckdb
con = duckdb.connect()

# Pega última versão de cada artigo
df = con.execute("""
  WITH ranked AS (
    SELECT *, 
           ROW_NUMBER() OVER (PARTITION BY url ORDER BY scraped_at DESC) as rn
    FROM read_parquet('data/processed/articles/**/*.parquet')
  )
  SELECT * FROM ranked WHERE rn = 1
""").df()
```

### 2. Deduplicação offline (compactação)

Periodicamente, compacte o dataset removendo duplicatas:

```python
import duckdb
from pathlib import Path

dataset_dir = Path("data/processed/articles")
output_dir = Path("data/processed/articles_deduplicated")

con = duckdb.connect()

# Lê tudo e deduplica
con.execute(f"""
  COPY (
    WITH ranked AS (
      SELECT *, 
             ROW_NUMBER() OVER (PARTITION BY url ORDER BY scraped_at DESC) as rn
      FROM read_parquet('{dataset_dir}/**/*.parquet')
    )
    SELECT * EXCEPT(rn) FROM ranked WHERE rn = 1
  )
  TO '{output_dir}' 
  (FORMAT PARQUET, PARTITION_BY (year, month, day, source), OVERWRITE_OR_IGNORE)
""")

print(f"Dataset deduplificado em {output_dir}")
```

### 3. Deduplicação no scraping (verificar antes de inserir)

Se quiser evitar duplicatas desde o início:

```python
import duckdb
from pathlib import Path

def url_exists(dataset_dir: Path, url: str) -> bool:
    if not dataset_dir.exists():
        return False
    
    con = duckdb.connect()
    result = con.execute(
        "SELECT count(*) FROM read_parquet(?) WHERE url = ?",
        [str(dataset_dir / "**" / "*.parquet"), url]
    ).fetchone()[0]
    return result > 0

# No scraping:
# if not url_exists(dataset_dir, url):
#     # scrape...
```

**Atenção**: essa verificação pode ser lenta em datasets grandes. Prefira deduplicar na consulta/análise.

## Recomendação para análise de sentimento

Para análise temporal comparando com eventos:

1. **Mantenha duplicatas** no dataset bruto (histórico completo).
2. **Deduplique na exportação** para análise (SQL acima).
3. Use `scraped_at` para rastrear quando foi coletado, mas `date_published` para agrupar temporalmente.

Exemplo:

```python
# Exporta apenas última versão de cada URL para análise
import duckdb
con = duckdb.connect()

df = con.execute("""
  WITH deduplicated AS (
    SELECT *, 
           ROW_NUMBER() OVER (PARTITION BY url ORDER BY scraped_at DESC) as rn
    FROM read_parquet('data/processed/articles/**/*.parquet')
    WHERE date_published >= '2020-01-01' AND date_published < '2020-02-01'
  )
  SELECT url, title, text, source, date_published
  FROM deduplicated 
  WHERE rn = 1
""").df()

df.to_json('janeiro_2020_deduplicated.jsonl', orient='records', lines=True)
```
