# Yahoo Finance Brasil - Guia de Coleta

## Sobre

Yahoo Finance Brasil (https://br.finance.yahoo.com) é uma excelente fonte para análise de sentimento correlacionada com mercado financeiro:
- Notícias sobre empresas, bolsa, economia
- Bom para correlacionar sentimento com preços de ações
- Cobertura de eventos financeiros (IPOs, balanços, crises)

## Características técnicas

- **Estrutura**: Site usa JavaScript para carregar conteúdo (SPA - Single Page Application)
- **URLs de notícias**: `https://br.finance.yahoo.com/noticias/*`
- **RSS**: Não disponível publicamente
- **Sitemap**: Não acessível diretamente

## Estratégias de coleta

### 1. Scraping de página de listagem

Como o site usa JavaScript, a melhor abordagem é usar o comando `historical archive`:

```bash
# Extrai links da página de notícias atual
news-scraper historical archive \
  --url "https://br.finance.yahoo.com/noticias/" \
  --out data/raw/yahoo_finance_links.txt

# Depois scrape
news-scraper scrape \
  --input data/raw/yahoo_finance_links.txt \
  --dataset-dir data/processed/articles \
  --delay 2.0
```

### 2. URLs conhecidas (teste manual primeiro)

Para testar, cole URLs de artigos manualmente:

```bash
# Crie arquivo com URLs de teste
cat > data/raw/yahoo_test.txt << 'EOF'
https://br.finance.yahoo.com/noticias/exemplo-noticia-1.html
https://br.finance.yahoo.com/noticias/exemplo-noticia-2.html
EOF

# Teste scraping
news-scraper scrape \
  --input data/raw/yahoo_test.txt \
  --out outputs/yahoo_test.jsonl \
  --delay 2.0
```

### 3. Fontes alternativas (mais confiáveis para histórico)

Para análise histórica, considere fontes que facilitam acesso ao arquivo:

**Notícias financeiras brasileiras com histórico:**
- **InfoMoney** (https://www.infomoney.com.br) - Tem sitemap e RSS
- **Valor Econômico** (https://valor.globo.com) - Estrutura por data
- **Bloomberg Brasil** (https://www.bloomberg.com.br) - RSS disponível
- **CNN Brasil Business** (https://www.cnnbrasil.com.br/business/) - Sitemap

## Exemplo prático: InfoMoney (alternativa recomendada)

InfoMoney tem melhor estrutura para coleta histórica:

```bash
# 1. Adicionar fonte
news-scraper sources add \
  --id infomoney \
  --name "InfoMoney" \
  --type rss \
  --url "https://www.infomoney.com.br/feed/"

# 2. Coletar de RSS (últimos artigos)
news-scraper rss \
  --feed "https://www.infomoney.com.br/feed/" \
  --scrape \
  --dataset-dir data/processed/articles \
  --limit 50

# 3. Para histórico, use sitemap
news-scraper historical sitemap \
  --url "https://www.infomoney.com.br/sitemap.xml" \
  --out data/raw/infomoney_all.txt

# 4. Filtre por período desejado (2020)
grep "/2020/" data/raw/infomoney_all.txt > data/raw/infomoney_2020.txt

# 5. Scrape histórico
news-scraper scrape \
  --input data/raw/infomoney_2020.txt \
  --dataset-dir data/processed/articles \
  --delay 2.0 \
  --max 500
```

## Caso de uso: Análise de sentimento vs. Ibovespa

### Objetivo
Correlacionar sentimento de notícias com variações do Ibovespa em 2020 (COVID-19).

### Passo 1: Coletar notícias de janeiro-março 2020

```bash
# InfoMoney (mais fácil)
news-scraper historical sitemap \
  --url "https://www.infomoney.com.br/sitemap.xml" \
  --filter "/2020/0" \
  --out data/raw/infomoney_jan_mar_2020.txt

# Filtrar apenas janeiro-março
grep -E "/(2020/01|2020/02|2020/03)/" data/raw/infomoney_jan_mar_2020.txt > data/raw/q1_2020.txt

# Scrape
news-scraper scrape \
  --input data/raw/q1_2020.txt \
  --dataset-dir data/processed/articles \
  --delay 2.0
```

### Passo 2: Consultar por período da queda (fevereiro-março 2020)

```bash
news-scraper query --dataset-dir data/processed/articles \
  --sql "SELECT date(date_published) as dia, count(*) as total, 
         source 
         FROM articles 
         WHERE date_published >= '2020-02-20' 
           AND date_published <= '2020-03-23'
         GROUP BY dia, source 
         ORDER BY dia" \
  --format csv > crash_covid_timeline.csv
```

### Passo 3: Exportar para análise de sentimento

```bash
news-scraper query --dataset-dir data/processed/articles \
  --sql "SELECT url, title, text, date_published, source 
         FROM articles 
         WHERE date_published >= '2020-02-20' 
           AND date_published <= '2020-03-23'
           AND text IS NOT NULL
         ORDER BY date_published" \
  --format json > crash_covid_articles.jsonl
```

### Passo 4: Análise de sentimento (Python)

```python
import pandas as pd
import json
from transformers import pipeline

# Carrega artigos
df = pd.read_json('crash_covid_articles.jsonl', lines=True)
df['date'] = pd.to_datetime(df['date_published']).dt.date

# Sentimento (modelo multilingual)
sentiment_pipeline = pipeline('sentiment-analysis', 
                              model='nlptown/bert-base-multilingual-uncased-sentiment')

def get_sentiment_score(text):
    if not text or len(text) < 10:
        return None
    result = sentiment_pipeline(text[:512])[0]
    # Converte para -1 a 1
    label = result['label']  # '1 star' a '5 stars'
    stars = int(label.split()[0])
    return (stars - 3) / 2  # -1 (negativo) a +1 (positivo)

df['sentiment'] = df['text'].apply(get_sentiment_score)

# Agrupa por dia
daily = df.groupby('date')['sentiment'].mean().reset_index()
daily.columns = ['date', 'sentiment_avg']

print(daily)

# Salva para correlacionar com Ibovespa
daily.to_csv('sentimento_diario.csv', index=False)
```

### Passo 5: Correlação com Ibovespa

```python
import yfinance as yf

# Baixa dados do Ibovespa
ibov = yf.download('^BVSP', start='2020-02-20', end='2020-03-24')
ibov['date'] = ibov.index.date
ibov = ibov.reset_index()[['date', 'Close']]
ibov.columns = ['date', 'ibovespa']

# Merge com sentimento
merged = pd.merge(daily, ibov, on='date', how='inner')

# Correlação
print(f"Correlação sentimento vs Ibovespa: {merged['sentiment_avg'].corr(merged['ibovespa']):.3f}")

# Plot
import matplotlib.pyplot as plt
fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.set_xlabel('Data')
ax1.set_ylabel('Sentimento', color='blue')
ax1.plot(merged['date'], merged['sentiment_avg'], color='blue', label='Sentimento')
ax1.tick_params(axis='y', labelcolor='blue')

ax2 = ax1.twinx()
ax2.set_ylabel('Ibovespa', color='red')
ax2.plot(merged['date'], merged['ibovespa'], color='red', label='Ibovespa')
ax2.tick_params(axis='y', labelcolor='red')

plt.title('Sentimento de Notícias vs. Ibovespa (Crash COVID-19)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('sentimento_ibovespa.png')
```

## Fontes recomendadas para análise financeira

Adicione ao `configs/sources.csv`:

```csv
enabled,source_id,name,type,url,tags
1,infomoney,InfoMoney,rss,https://www.infomoney.com.br/feed/,financas;mercado
1,cnnbrasil_business,CNN Brasil Business,rss,https://www.cnnbrasil.com.br/business/feed/,financas;economia
1,valor,Valor Econômico,rss,https://valor.globo.com/rss,financas;mercado
```

Depois:
```bash
news-scraper rss --sources-csv configs/sources.csv --scrape \
  --dataset-dir data/processed/articles
```

## Limitações do Yahoo Finance Brasil

- JavaScript-heavy (dificulta scraping direto)
- Sem RSS público
- Sem sitemap acessível
- URLs podem mudar estrutura

**Recomendação**: Use InfoMoney ou Valor como fontes principais para histórico, e Yahoo Finance apenas para artigos específicos que você já tem URLs.
