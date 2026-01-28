# Exemplo prático: Análise de sentimento de notícias financeiras vs. Ibovespa

Este exemplo demonstra o fluxo completo para correlacionar sentimento de notícias financeiras com variações do mercado.

## Cenário: Crash do COVID-19 (fevereiro-março 2020)

Vamos analisar como o sentimento das notícias variou durante a queda histórica do Ibovespa em março de 2020.

## Passo 1: Configurar fontes financeiras

```bash
cd /Users/wagnermontes/Documents/GitHub/news-scraper

# Fontes já estão em configs/sources.csv
news-scraper sources list
```

## Passo 2: Coletar notícias históricas (Q1 2020)

### Opção A: Via sitemap (recomendado para histórico)

```bash
# InfoMoney
news-scraper historical sitemap \
  --url "https://www.infomoney.com.br/sitemap.xml" \
  --filter "/2020/" \
  --out data/raw/infomoney_2020.txt

# Filtrar apenas jan-mar
grep -E "/(2020/01|2020/02|2020/03)/" data/raw/infomoney_2020.txt > data/raw/infomoney_q1_2020.txt

# Scrape
news-scraper scrape \
  --input data/raw/infomoney_q1_2020.txt \
  --dataset-dir data/processed/articles \
  --delay 2.0 \
  --max 300
```

### Opção B: Gerar URLs por padrão de data

```bash
# Se souber o padrão de URL do site
news-scraper historical generate \
  --pattern "https://www.infomoney.com.br/{YYYY}/{MM}/{DD}/" \
  --start 2020-02-01 \
  --end 2020-03-31 \
  --out data/raw/infomoney_urls_q1.txt

# Extrair artigos de cada página de arquivo
while read url; do
  news-scraper historical archive --url "$url" --out temp_links.txt
  cat temp_links.txt >> data/raw/all_articles.txt
done < data/raw/infomoney_urls_q1.txt

# Deduplica
sort -u data/raw/all_articles.txt > data/raw/articles_unique.txt

# Scrape
news-scraper scrape \
  --input data/raw/articles_unique.txt \
  --dataset-dir data/processed/articles
```

## Passo 3: Verificar coleta

```bash
news-scraper stats --dataset-dir data/processed/articles

news-scraper query --dataset-dir data/processed/articles \
  --sql "SELECT date(date_published) as dia, count(*) 
         FROM articles 
         WHERE date_published BETWEEN '2020-02-01' AND '2020-03-31'
         GROUP BY dia 
         ORDER BY dia"
```

## Passo 4: Exportar período do crash

```bash
# Crash principal: 20 fev - 23 mar 2020
news-scraper query --dataset-dir data/processed/articles \
  --sql "SELECT url, title, text, date_published, source 
         FROM articles 
         WHERE date_published >= '2020-02-20' 
           AND date_published <= '2020-03-23'
           AND text IS NOT NULL
         ORDER BY date_published" \
  --format json > data/interim/crash_covid_articles.jsonl

echo "Artigos exportados: $(wc -l < data/interim/crash_covid_articles.jsonl)"
```

## Passo 5: Análise de sentimento

Crie `analysis/sentiment_analysis.py`:

```python
import pandas as pd
from transformers import pipeline
import yfinance as yf
import matplotlib.pyplot as plt

# Carrega artigos
df = pd.read_json('data/interim/crash_covid_articles.jsonl', lines=True)
df['date'] = pd.to_datetime(df['date_published']).dt.date

print(f"Total de artigos: {len(df)}")

# Pipeline de sentimento (português/multilingual)
sentiment_model = pipeline(
    'sentiment-analysis',
    model='nlptown/bert-base-multilingual-uncased-sentiment'
)

def calculate_sentiment(text):
    """Converte sentiment para score -1 a +1"""
    if not text or len(text) < 20:
        return None
    try:
        result = sentiment_model(text[:512])[0]
        stars = int(result['label'].split()[0])  # '1 star' -> 1
        # 1 star = -1 (muito negativo), 5 stars = +1 (muito positivo)
        return (stars - 3) / 2
    except:
        return None

print("Calculando sentimento...")
df['sentiment'] = df['text'].apply(calculate_sentiment)
df = df[df['sentiment'].notna()]  # Remove falhas

print(f"Artigos com sentimento: {len(df)}")

# Agrupa por dia
daily_sentiment = df.groupby('date').agg({
    'sentiment': ['mean', 'std', 'count']
}).reset_index()
daily_sentiment.columns = ['date', 'sentiment_avg', 'sentiment_std', 'article_count']

print("\nSentimento diário:")
print(daily_sentiment.head(10))

# Baixa Ibovespa
ibov = yf.download('^BVSP', start='2020-02-20', end='2020-03-24', progress=False)
ibov['date'] = ibov.index.date
ibov = ibov.reset_index()[['date', 'Close']]
ibov.columns = ['date', 'ibovespa_close']

# Calcula variação percentual
ibov['ibovespa_pct'] = ibov['ibovespa_close'].pct_change() * 100

# Merge
merged = pd.merge(daily_sentiment, ibov, on='date', how='inner')

print(f"\nCorrelação sentimento vs variação Ibovespa: {merged['sentiment_avg'].corr(merged['ibovespa_pct']):.3f}")

# Salva
merged.to_csv('data/interim/sentimento_ibovespa_diario.csv', index=False)

# Plot
fig, ax1 = plt.subplots(figsize=(14, 7))

ax1.set_xlabel('Data', fontsize=12)
ax1.set_ylabel('Sentimento médio', color='blue', fontsize=12)
ax1.plot(merged['date'], merged['sentiment_avg'], 
         color='blue', marker='o', label='Sentimento', linewidth=2)
ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax1.tick_params(axis='y', labelcolor='blue')
ax1.grid(alpha=0.3)

ax2 = ax1.twinx()
ax2.set_ylabel('Ibovespa (pontos)', color='red', fontsize=12)
ax2.plot(merged['date'], merged['ibovespa_close'], 
         color='red', marker='s', label='Ibovespa', linewidth=2)
ax2.tick_params(axis='y', labelcolor='red')

plt.title('Sentimento de Notícias Financeiras vs. Ibovespa\nCrash COVID-19 (fev-mar 2020)', 
          fontsize=14, fontweight='bold')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('outputs/sentimento_ibovespa_crash.png', dpi=300)
print("\nGráfico salvo: outputs/sentimento_ibovespa_crash.png")
```

Execute:
```bash
python analysis/sentiment_analysis.py
```

## Passo 6: Análise estatística

```python
import pandas as pd
from scipy.stats import pearsonr

df = pd.read_csv('data/interim/sentimento_ibovespa_diario.csv')

# Correlação (lag 0 - mesmo dia)
corr, pvalue = pearsonr(df['sentiment_avg'].dropna(), 
                        df['ibovespa_pct'].dropna())
print(f"Correlação (mesmo dia): {corr:.3f} (p={pvalue:.4f})")

# Lag +1 (sentimento prevê próximo dia)
df['ibovespa_pct_next'] = df['ibovespa_pct'].shift(-1)
corr_lag1, pvalue_lag1 = pearsonr(
    df['sentiment_avg'].iloc[:-1], 
    df['ibovespa_pct_next'].iloc[:-1]
)
print(f"Correlação (lag +1 dia): {corr_lag1:.3f} (p={pvalue_lag1:.4f})")
```

## Insights esperados

Durante o crash COVID-19:
- **Sentimento negativo** correlaciona com quedas do Ibovespa
- **Volatilidade aumentada** em ambos
- **Lag effects**: sentimento pode preceder movimentos (ou vice-versa)

## Próximos passos

1. **Ampliar período**: coletar 2019-2021 completo
2. **Tópicos**: filtrar apenas notícias sobre "covid", "quarentena", "lockdown"
3. **Múltiplas fontes**: agregar InfoMoney + Valor + outros
4. **Empresas específicas**: analisar sentimento sobre Petrobras, Vale, etc.
5. **Modelos preditivos**: usar sentimento como feature para prever retornos
