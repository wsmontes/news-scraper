# Coleta histórica (períodos passados)

RSS é limitado a artigos recentes (últimos dias/semanas). Para análise de sentimento comparando com eventos passados, você precisa coletar notícias históricas.

## Estratégias para períodos passados

### 1. Sitemaps XML

Muitos sites têm sitemaps que listam **todas** as URLs, incluindo antigas.

**Encontrar sitemap:**
```
https://example.com/sitemap.xml
https://example.com/sitemap_index.xml
https://example.com/robots.txt  (geralmente lista o sitemap)
```

**Extrair URLs:**
```bash
news-scraper historical sitemap \
  --url https://example.com/sitemap.xml \
  --filter "/2020/" \
  --out data/raw/urls_2020.txt

# Depois scrape
news-scraper scrape --input data/raw/urls_2020.txt \
  --dataset-dir data/processed/articles
```

### 2. Padrões de URL por data

Muitos sites organizam URLs por data. Descubra o padrão e gere lista automaticamente.

**Exemplos de padrões comuns:**
- `https://site.com/2020/01/15/titulo-noticia/`
- `https://site.com/noticia/20200115/...`
- `https://site.com/arquivo/2020/01/15/`

**Descobrir padrão:**
1. Acesse uma notícia antiga do site
2. Observe a estrutura da URL
3. Identifique onde estão ano/mês/dia

**Gerar URLs:**
```bash
# Por dia
news-scraper historical generate \
  --pattern "https://example.com/arquivo/{YYYY}/{MM}/{DD}/" \
  --start 2020-01-01 \
  --end 2020-01-31 \
  --out data/raw/urls_jan2020.txt

# Por mês (para páginas de arquivo mensal)
news-scraper historical generate \
  --pattern "https://example.com/arquivo/{YYYY}/{MM}/" \
  --start 2020-01-01 \
  --end 2020-12-31 \
  --by-month \
  --out data/raw/archives_2020.txt
```

**Placeholders suportados:**
- `{YYYY}` - ano (4 dígitos)
- `{MM}` - mês com zero (01-12)
- `{DD}` - dia com zero (01-31)
- `{M}` - mês sem zero (1-12)
- `{D}` - dia sem zero (1-31)

### 3. Páginas de arquivo

Alguns sites têm páginas que listam artigos por período.

**Exemplos:**
- `https://site.com/arquivo/2020/janeiro/`
- `https://site.com/noticias?data=2020-01`

**Extrair links:**
```bash
news-scraper historical archive \
  --url "https://example.com/arquivo/2020/01/" \
  --out data/raw/links_jan2020.txt
```

### 4. APIs e dados públicos

Alguns portais disponibilizam APIs ou datasets históricos:
- **Kaggle**: datasets de notícias brasileiras
- **Internet Archive**: snapshots de sites antigos
- **APIs oficiais**: G1, Folha, etc. (verifique documentação)

## Exemplo completo: eleições 2020

Objetivo: coletar notícias sobre eleições municipais (outubro-novembro 2020).

### Passo 1: Identificar fontes e padrões

```bash
# Exemplo: G1 usa padrão /YYYY/MM/DD/
# Folha usa padrão /YYYY/MM/
```

### Passo 2: Gerar URLs para o período

```bash
# G1 - páginas de arquivo diárias
news-scraper historical generate \
  --pattern "https://g1.globo.com/politica/{YYYY}/{MM}/{DD}/" \
  --start 2020-10-01 \
  --end 2020-11-30 \
  --out data/raw/g1_eleicoes2020_archives.txt

# Ou usar sitemap
news-scraper historical sitemap \
  --url https://g1.globo.com/sitemap.xml \
  --filter "/politica/eleicoes/2020/" \
  --out data/raw/g1_eleicoes2020_sitemap.txt
```

### Passo 3: Extrair artigos das páginas de arquivo

Se as URLs geradas são páginas de arquivo (listam links), extraia:

```bash
# Ler cada URL de arquivo e extrair links de artigos
while read url; do
  news-scraper historical archive --url "$url" --out data/raw/temp_links.txt
  cat data/raw/temp_links.txt >> data/raw/todos_artigos_eleicoes.txt
done < data/raw/g1_eleicoes2020_archives.txt

# Remove duplicatas
sort -u data/raw/todos_artigos_eleicoes.txt > data/raw/artigos_eleicoes_uniq.txt
```

### Passo 4: Scrape dos artigos

```bash
news-scraper scrape \
  --input data/raw/artigos_eleicoes_uniq.txt \
  --dataset-dir data/processed/articles \
  --delay 2.0 \
  --max 1000
```

### Passo 5: Validar período coletado

```bash
news-scraper stats --dataset-dir data/processed/articles

news-scraper query --dataset-dir data/processed/articles \
  --sql "SELECT date(date_published) as dia, count(*) FROM articles 
         WHERE date_published >= '2020-10-01' AND date_published <= '2020-11-30'
         GROUP BY dia ORDER BY dia"
```

## Dicas importantes

### Rate limiting para histórico

Coleta histórica pode ser volumosa. Use delays maiores:
```bash
--delay 2.0  # ou mais, para não sobrecarregar o servidor
```

### Resumir antes de baixar tudo

Teste com amostra pequena primeiro:
```bash
head -n 100 urls.txt > urls_teste.txt
news-scraper scrape --input urls_teste.txt --out teste.jsonl
```

### Verificar robots.txt

Mesmo para histórico, respeite:
```bash
curl https://example.com/robots.txt
```

### Paralelizar com cuidado

Para muitas URLs, divida em lotes:
```bash
split -l 1000 urls.txt lote_
for lote in lote_*; do
  news-scraper scrape --input "$lote" \
    --dataset-dir data/processed/articles \
    --delay 2.0
  sleep 300  # pausa entre lotes
done
```

## Limitações e alternativas

### Sites que mudaram de estrutura

URLs antigas podem retornar 404. Estratégias:
- Use Internet Archive Wayback Machine
- Busque versões arquivadas do site
- Contate o veículo para acesso a arquivo histórico

### Paywall

Artigos pagos não serão extraídos. Alternativas:
- Use apenas manchete/resumo (quando disponível)
- Acesso institucional (universidades têm convênios)
- Fontes abertas (agências públicas, blogs acadêmicos)

### Volume muito grande

Para milhares de artigos:
- Use amostragem (ex.: 1 artigo a cada 5 dias)
- Foque em eventos específicos (janelas de tempo menores)
- Considere usar serviços pagos (NewsAPI, GDELT, etc.)
