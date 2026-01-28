# Teste profissional: InfoMoney com Browser Scraping

Este exemplo demonstra scraping profissional com Selenium para sites JavaScript-heavy.

## InfoMoney (mais confiável que Yahoo Finance)

InfoMoney tem estrutura mais acessível e funciona bem com scraping.

### Teste 1: Extrair URLs da página de notícias

```bash
# Usar scraper customizado para InfoMoney
news-scraper browser custom \
  --url "https://www.infomoney.com.br/mercados/" \
  --selector "a[href*='/mercados/']" \
  --filter "/mercados/" \
  --out data/raw/infomoney_mercados.txt \
  --headless

# Ver URLs coletadas
cat data/raw/infomoney_mercados.txt | head -10
```

### Teste 2: Scrape completo com dataset

```bash
# 1. Extrair URLs
news-scraper browser custom \
  --url "https://www.infomoney.com.br/ultimas-noticias/" \
  --selector "article a" \
  --out data/raw/infomoney_latest.txt \
  --headless

# 2. Scrape os artigos
news-scraper scrape \
  --input data/raw/infomoney_latest.txt \
  --dataset-dir data/processed/articles \
  --delay 2.0 \
  --max 20

# 3. Ver estatísticas
news-scraper stats --dataset-dir data/processed/articles
```

## Alternativa: Sites mais simples para teste

### Valor Econômico

```bash
# Valor tem boa estrutura
news-scraper browser custom \
  --url "https://valor.globo.com/ultimas-noticias/" \
  --selector "a.feed-post-link" \
  --out data/raw/valor_latest.txt \
  --headless
```

### G1 Economia

```bash
news-scraper browser custom \
  --url "https://g1.globo.com/economia/" \
  --selector "a.feed-post-link" \
  --filter "/economia/" \
  --out data/raw/g1_economia.txt \
  --headless
```

## Yahoo Finance: Limitação conhecida

Yahoo Finance Brasil tem proteção anti-scraping forte:
- Redireciona para página de busca
- Requer cookies/session complexos
- Muda estrutura frequentemente

**Solução recomendada:**
1. Use InfoMoney ou Valor para notícias financeiras brasileiras
2. Para Yahoo Finance, use APIs oficiais quando disponíveis
3. Ou colete manualmente URLs específicas e scrape depois

## Script de teste completo

```bash
#!/bin/bash
# Teste profissional com InfoMoney

mkdir -p data/raw

echo "1. Coletando URLs com browser scraping..."
news-scraper browser custom \
  --url "https://www.infomoney.com.br/ultimas-noticias/" \
  --selector "a[href*='/20']" \
  --filter "infomoney.com.br" \
  --out data/raw/infomoney_urls.txt \
  --headless

count=$(wc -l < data/raw/infomoney_urls.txt)
echo "✓ $count URLs coletadas"

if [ "$count" -gt 0 ]; then
    echo ""
    echo "2. Scraping artigos..."
    news-scraper scrape \
      --input data/raw/infomoney_urls.txt \
      --dataset-dir data/processed/articles \
      --delay 2.0 \
      --max 10

    echo ""
    echo "3. Estatísticas:"
    news-scraper stats --dataset-dir data/processed/articles

    echo ""
    echo "4. Consultar artigos:"
    news-scraper query --dataset-dir data/processed/articles \
      --sql "SELECT title, date_published FROM articles LIMIT 5"
fi
```

## Para produção: estratégias avançadas

### 1. Rotação de User-Agents

```python
from news_scraper.browser import BrowserConfig, ProfessionalScraper

user_agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
]

for i, ua in enumerate(user_agents):
    config = BrowserConfig(user_agent=ua)
    with ProfessionalScraper(config) as scraper:
        urls = scraper.extract_links(...)
```

### 2. Delays inteligentes

```python
import random
import time

for url in urls:
    scrape(url)
    delay = random.uniform(2.0, 5.0)  # randomiza delay
    time.sleep(delay)
```

### 3. Retry com backoff

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def scrape_with_retry(url):
    return scraper.get_page(url)
```

### 4. Proxies (se necessário)

```python
# Adicionar proxy no ChromeOptions
options.add_argument('--proxy-server=http://proxy:port')
```
