# Exemplo Completo: Workflow Profissional de News Scraping

Este documento demonstra o fluxo de trabalho completo, do zero até análise de dados.

## Demonstração testada com InfoMoney

### 1. Extrair URLs com Browser Scraping

```bash
# Criar script Python para extrair URLs
cat > scripts/extract_infomoney.py << 'EOF'
from news_scraper.browser import BrowserConfig, ProfessionalScraper

config = BrowserConfig(headless=True)
with ProfessionalScraper(config) as scraper:
    print("Carregando homepage do InfoMoney...")
    scraper.get_page('https://www.infomoney.com.br/', wait_time=3)
    
    print("Scrolling para carregar mais conteúdo...")
    scraper.scroll_and_load(scroll_pause=1.5, max_scrolls=3)
    
    all_links = scraper.driver.find_elements('css selector', 'a')
    
    article_urls = []
    for link in all_links:
        href = link.get_attribute('href')
        # Filtrar apenas artigos de mercados (URLs longas)
        if href and '/mercados/' in href and len(href) > 60:
            article_urls.append(href)
    
    # Deduplicate e limitar
    article_urls = sorted(set(article_urls))[:20]
    
    # Salvar em arquivo
    with open('data/raw/infomoney_urls.txt', 'w') as f:
        f.write('\n'.join(article_urls))
    
    print(f"\n✓ {len(article_urls)} URLs salvas em data/raw/infomoney_urls.txt")
EOF

# Executar
python scripts/extract_infomoney.py
```

**Resultado esperado:**
```
Carregando homepage do InfoMoney...
Scrolling para carregar mais conteúdo...

✓ 20 URLs salvas em data/raw/infomoney_urls.txt
```

### 2. Scrape dos artigos para dataset Parquet

```bash
# Scraping com delays polidos e salvamento direto em Parquet
news-scraper scrape \
  --input data/raw/infomoney_urls.txt \
  --dataset-dir data/processed/articles \
  --delay 2.0 \
  --max 20

# Tempo estimado: ~40 segundos (20 artigos × 2s delay)
```

**Resultado esperado:**
```
Scraping: 100%|████████████████| 20/20 [00:40<00:00,  2.01s/it]
```

### 3. Verificar estatísticas do dataset

```bash
news-scraper stats --dataset-dir data/processed/articles
```

**Resultado esperado:**
```
Total de artigos: 20

Artigos por fonte:
  www.infomoney.com.br: 20

Período:
```

### 4. Consultar os dados com SQL

#### Ver títulos e tamanhos de texto

```bash
news-scraper query \
  --dataset-dir data/processed/articles \
  --sql "SELECT title, LENGTH(text) as chars FROM articles LIMIT 5"
```

#### Filtrar por palavra-chave

```bash
news-scraper query \
  --dataset-dir data/processed/articles \
  --sql "SELECT title FROM articles WHERE text LIKE '%dólar%' OR text LIKE '%câmbio%'"
```

#### Exportar para CSV para análise de sentimento

```bash
news-scraper query \
  --dataset-dir data/processed/articles \
  --sql "SELECT title, text, scraped_at FROM articles" \
  --format csv > data/analysis/infomoney_export.csv
```

## Estrutura do dataset criado

```
data/processed/articles/
├── source=www.infomoney.com.br/
│   └── [arquivos .parquet]
```

**Cada artigo contém:**
- `url`: URL completa
- `title`: Título extraído
- `text`: Texto completo do artigo
- `author`: Autor (se disponível)
- `date_published`: Data publicação (se disponível)
- `scraped_at`: Timestamp da coleta
- `language`: Idioma detectado
- `source`: Domínio fonte
- `extra`: Metadados adicionais (JSON)

## Análise de sentimento (próximo passo)

Com os dados em Parquet/CSV, você pode:

### 1. Carregar em Python

```python
import duckdb

conn = duckdb.connect(database=':memory:')
df = conn.execute("""
    SELECT title, text, scraped_at 
    FROM read_parquet('data/processed/articles/**/*.parquet')
""").df()

print(f"Loaded {len(df)} articles")
```

### 2. Aplicar modelo de sentimento

```python
from transformers import pipeline

sentiment = pipeline("sentiment-analysis", 
                    model="lucas-leme/FinBERT-PT-BR")

for idx, row in df.iterrows():
    text_sample = row['text'][:512]  # Limite de tokens
    result = sentiment(text_sample)
    print(f"{row['title']}: {result[0]['label']}")
```

### 3. Correlacionar com eventos

```python
import pandas as pd

# Adicionar coluna de data
df['date'] = pd.to_datetime(df['scraped_at']).dt.date

# Eventos importantes
events = {
    '2024-05-15': 'Anúncio fiscal',
    '2024-11-05': 'Eleições EUA',
}

# Análise temporal
for event_date, event_name in events.items():
    week_before = df[df['date'].between(
        event_date - pd.Timedelta(days=7), 
        event_date
    )]
    print(f"\n{event_name} ({event_date}):")
    print(f"  Artigos na semana anterior: {len(week_before)}")
```

## Coleta histórica

Para coletar notícias de períodos passados, use URLs específicas:

```bash
# Exemplo: página de arquivo por data
news-scraper browser custom \
  --url "https://www.infomoney.com.br/2024/05/" \
  --selector "article a" \
  --filter "/mercados/" \
  --out data/raw/infomoney_maio2024.txt \
  --headless
```

Ou crie um scraper customizado para navegar por páginas de arquivo.

## Troubleshooting

### "0 URLs extraídas"

- Verifique o filtro (`--filter`)
- Inspecione o HTML da página manualmente
- Teste sem headless (`--headless false`) para ver o navegador

### "404 Not Found"

- URLs podem expirar rapidamente
- Colete URLs frescas direto da homepage
- Use sitemaps quando disponíveis

### "Text length: 0"

- Site pode requerer JavaScript (use browser scraping)
- Verifique se trafilatura reconhece a estrutura
- Teste extração manual com BeautifulSoup

## Comparação de abordagens

| Método | Velocidade | Histórico | Cobertura | Complexidade |
|--------|-----------|-----------|-----------|-------------|
| **RSS** | ⚡⚡⚡ Rápido | ❌ Só últimos 7 dias | 🔸 ~30 artigos | ✅ Simples |
| **Sitemap** | ⚡⚡ Médio | ✅ Anos completos | ⭐⭐⭐ Completo | ✅ Simples |
| **Browser Scraping** | ⚡ Lento | 🔸 Depende | ⭐⭐ Bom | 🔸 Médio |
| **API oficial** | ⚡⚡⚡ Rápido | ✅ Configurável | ⭐⭐⭐ Completo | 💰 Pago |

**Recomendação para projeto acadêmico:**
1. Comece com RSS para teste rápido
2. Use Sitemap para coleta histórica massiva
3. Browser Scraping apenas para sites sem sitemap
4. APIs pagas se orçamento permitir

## Próximos passos

1. [ ] Configurar múltiplas fontes no `configs/sources.csv`
2. [ ] Implementar coleta histórica sistemática
3. [ ] Integrar modelo de análise de sentimento
4. [ ] Criar pipeline de correlação com eventos financeiros
5. [ ] Dashboard de visualização (Streamlit/Dash)
