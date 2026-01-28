# Exemplo: workflow completo para análise de sentimento

Este exemplo mostra o fluxo end-to-end do scraping até a preparação para análise.

## 1. Configurar fontes

Edite `configs/sources.csv` ou use a CLI:

```bash
news-scraper sources add --id g1 --name "G1" --type rss \
  --url "https://g1.globo.com/rss/g1/" --tags "brasil;geral"

news-scraper sources add --id folha --name "Folha" --type rss \
  --url "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml" --tags "brasil"
```

## 2. Coletar notícias de RSS

Raspar artigos dos feeds configurados:

```bash
news-scraper rss --sources-csv configs/sources.csv \
  --scrape \
  --dataset-dir data/processed/articles \
  --limit 50
```

Isso cria partições em `data/processed/articles/year=YYYY/month=MM/day=DD/source=<fonte>/`.

## 3. Ver estatísticas

```bash
news-scraper stats --dataset-dir data/processed/articles
```

Exemplo de saída:
```
Total de artigos: 125

Artigos por fonte:
  g1: 80
  folha: 45

Período:
  Primeiro: 2026-01-15 10:30:00
  Último: 2026-01-27 14:22:00
```

## 4. Consultar por período (evento específico)

Supondo que você queira analisar notícias sobre um evento em 20-25 de janeiro:

```bash
news-scraper query --dataset-dir data/processed/articles \
  --sql "SELECT url, title, source, date_published FROM articles 
         WHERE date_published >= '2026-01-20' 
           AND date_published < '2026-01-26' 
         ORDER BY date_published" \
  --format json > evento_jan20-25.jsonl
```

## 5. Preparar para análise de sentimento

Com o JSONL exportado, você pode:

- **Pandas**:
  ```python
  import pandas as pd
  df = pd.read_json('evento_jan20-25.jsonl', lines=True)
  print(df[['title', 'text']].head())
  ```

- **Análise de sentimento** (exemplo com transformers):
  ```python
  from transformers import pipeline
  sentiment = pipeline('sentiment-analysis', model='nlptown/bert-base-multilingual-uncased-sentiment')
  
  for _, row in df.iterrows():
      if row['text']:
          result = sentiment(row['text'][:512])  # trunca para 512 tokens
          print(f"{row['title']}: {result}")
  ```

## 6. Comparar sentimento com eventos

Agrupe por data e calcule médias de sentimento, depois compare com datas de eventos:

```python
df['sentiment_score'] = df['text'].apply(lambda x: calcular_sentimento(x))
daily_sentiment = df.groupby(df['date_published'].dt.date)['sentiment_score'].mean()

# Compara com evento em 2026-01-23
print(f"Sentimento médio em 23/01: {daily_sentiment.get('2026-01-23', 'N/A')}")
```

## Notas

- Para **períodos longos**, faça múltiplas coletas ao longo do tempo.
- **Deduplicação**: o dataset particionado permite sobrescrever por URL se necessário (implemente lógica customizada).
- **Fontes adicionais**: além de RSS, considere sitemaps e arquivos históricos dos sites.
