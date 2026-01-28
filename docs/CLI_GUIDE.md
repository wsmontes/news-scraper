# Guia Completo do CLI

Este documento descreve todos os comandos disponíveis no `news-scraper` CLI.

## Índice

- [Comando `collect` (Novo!)](#comando-collect)
- [Comando `scrape`](#comando-scrape)
- [Comando `browser`](#comando-browser)
- [Comando `query`](#comando-query)
- [Outros Comandos](#outros-comandos)
- [Exemplos Práticos](#exemplos-práticos)

---

## Comando `collect`

**Comando unificado e completo para coletar notícias** de múltiplas fontes financeiras brasileiras.

### Sintaxe Básica

```bash
news-scraper collect --source FONTE [OPTIONS]
```

### Parâmetros Obrigatórios

| Parâmetro | Valores | Descrição |
|-----------|---------|-----------|
| `--source` | `infomoney`, `moneytimes`, `valor`, `bloomberg`, `einvestidor`, `all` | Fonte(s) para coletar (pode repetir) |

### Parâmetros de Filtro

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `--category` | string | Categoria específica (varia por fonte) |
| `--start-date` | YYYY-MM-DD | Data inicial para filtrar artigos |
| `--end-date` | YYYY-MM-DD | Data final para filtrar artigos |
| `--limit` | int | Máximo de artigos por fonte (padrão: 20) |

### Parâmetros de Saída

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `--dataset-dir` | path | Diretório do dataset Parquet (padrão: data/processed/articles) |
| `--urls-out` | path | Salvar URLs em arquivo .txt antes do scrape |

### Parâmetros de Configuração

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `--use-proxy` | flag | Ativar sistema inteligente de proxies |
| `--proxy-fallback` | flag | Fallback automático de proxy (padrão: ativo) |
| `--headless` | flag | Browser headless (padrão: ativo) |
| `--delay` | float | Delay entre requisições em segundos (padrão: 2.0) |
| `--skip-scrape` | flag | Apenas coletar URLs, não fazer scrape |
| `--verbose` | flag | Modo verboso com mais logs |

### Categorias por Fonte

**InfoMoney:**
- `mercados`, `economia`, `investimentos`, `negocios`, `carreira`

**Money Times:**
- Não possui categorias (sempre homepage)

**Valor Econômico:**
- `financas`, `empresas`, `mercados`, `mundo`, `politica`, `brasil`

**Bloomberg Brasil:**
- `mercados`, `economia`, `negocios`, `tecnologia`

**E-Investidor:**
- `mercados`, `investimentos`, `fundos-imobiliarios`, `cripto`, `acoes`

### Exemplos

#### 1. Coletar de uma fonte específica

```bash
news-scraper collect --source infomoney --category mercados --limit 10
```

#### 2. Coletar de múltiplas fontes

```bash
news-scraper collect \
  --source infomoney \
  --source moneytimes \
  --source valor \
  --limit 20
```

#### 3. Coletar de todas as fontes

```bash
news-scraper collect --source all --limit 15
```

#### 4. Coletar com filtro de período

```bash
news-scraper collect \
  --source all \
  --limit 50 \
  --start-date 2026-01-01 \
  --end-date 2026-01-28
```

#### 5. Coletar com proxies inteligentes

```bash
news-scraper collect \
  --source all \
  --limit 20 \
  --use-proxy \
  --verbose
```

#### 6. Apenas coletar URLs (sem scrape)

```bash
news-scraper collect \
  --source bloomberg \
  --category mercados \
  --limit 30 \
  --skip-scrape \
  --urls-out data/raw/bloomberg_urls.txt
```

#### 7. Workflow completo com delay e proxy

```bash
news-scraper collect \
  --source all \
  --category mercados \
  --limit 30 \
  --start-date 2026-01-20 \
  --end-date 2026-01-28 \
  --use-proxy \
  --proxy-fallback \
  --delay 3.0 \
  --urls-out data/raw/collected_urls.txt \
  --dataset-dir data/processed/weekly \
  --verbose
```

---

## Comando `scrape`

Extrai conteúdo de URLs já coletadas.

### Sintaxe

```bash
news-scraper scrape [--url URL | --input FILE] --out OUTPUT [OPTIONS]
```

### Exemplos

```bash
# Scrape de URL única
news-scraper scrape --url "https://..." --out articles.jsonl

# Scrape de arquivo com URLs
news-scraper scrape --input urls.txt --out articles.jsonl

# Direto para dataset Parquet
news-scraper scrape --input urls.txt --dataset-dir data/processed/articles
```

---

## Comando `browser`

Scraping específico por fonte usando Selenium.

### Subcomandos Disponíveis

- `infomoney` - InfoMoney
- `moneytimes` - Money Times
- `valor` - Valor Econômico
- `bloomberg` - Bloomberg Brasil
- `einvestidor` - E-Investidor
- `yahoo-finance` - Yahoo Finance
- `custom` - URL customizada

### Exemplos

```bash
# InfoMoney
news-scraper browser infomoney \
  --category mercados \
  --limit 20 \
  --out infomoney.txt \
  --scrape \
  --dataset-dir data/processed/articles

# Valor
news-scraper browser valor \
  --category mercados \
  --limit 15 \
  --out valor.txt

# Bloomberg
news-scraper browser bloomberg \
  --category economia \
  --limit 10 \
  --out bloomberg.txt \
  --scrape \
  --dataset-dir data/processed/articles

# Custom com seletor CSS
news-scraper browser custom \
  --url "https://site.com" \
  --selector "a.article" \
  --filter "/noticias/" \
  --out custom.txt
```

---

## Comando `query`

Executa consultas SQL no dataset Parquet usando DuckDB.

### Sintaxe

```bash
news-scraper query --dataset-dir DIR --sql "SQL_QUERY" [--format FORMAT]
```

### Formatos de Saída

- `table` - Tabela ASCII (padrão)
- `csv` - CSV para export
- `json` - JSON estruturado

### Exemplos

```bash
# Contar artigos por fonte
news-scraper query \
  --dataset-dir data/processed/articles \
  --sql "SELECT source, COUNT(*) as total FROM articles GROUP BY source"

# Artigos recentes
news-scraper query \
  --dataset-dir data/processed/articles \
  --sql "SELECT date, title, source FROM articles ORDER BY date DESC LIMIT 10"

# Filtrar por palavra-chave
news-scraper query \
  --dataset-dir data/processed/articles \
  --sql "SELECT title, source FROM articles WHERE LOWER(text) LIKE '%juros%' LIMIT 5"

# Export para CSV
news-scraper query \
  --dataset-dir data/processed/articles \
  --sql "SELECT * FROM articles WHERE date='2026-01-28'" \
  --format csv > resultado.csv
```

---

## Comando `stats`

Mostra estatísticas do dataset.

### Sintaxe

```bash
news-scraper stats --dataset-dir DIR
```

### Exemplo

```bash
news-scraper stats --dataset-dir data/processed/articles
```

Mostra:
- Total de artigos
- Distribuição por fonte
- Período de cobertura
- Tamanho do dataset

---

## Outros Comandos

### `rss` - Coletar de feeds RSS

```bash
news-scraper rss --feed "https://..." --out links.txt
```

### `sources` - Gerenciar fontes

```bash
# Listar
news-scraper sources list

# Adicionar
news-scraper sources add \
  --id myfeed \
  --name "Meu Feed" \
  --type rss \
  --url "https://..."

# Habilitar/Desabilitar
news-scraper sources enable myfeed
news-scraper sources disable myfeed
```

### `historical` - Ferramentas históricas

```bash
# Gerar URLs por padrão de data
news-scraper historical generate \
  --pattern "https://site.com/{YYYY}/{MM}/{DD}/" \
  --start 2025-01-01 \
  --end 2025-12-31 \
  --out historical_urls.txt

# Extrair de sitemap
news-scraper historical sitemap \
  --url "https://site.com/sitemap.xml" \
  --out sitemap_urls.txt
```

---

## Exemplos Práticos

### 1. Análise Semanal Completa

```bash
#!/bin/bash
# Coleta semanal de todas as fontes

# Coletar
news-scraper collect \
  --source all \
  --category mercados \
  --limit 50 \
  --start-date 2026-01-20 \
  --end-date 2026-01-28 \
  --dataset-dir data/weekly/2026-W04 \
  --use-proxy \
  --verbose

# Estatísticas
news-scraper stats --dataset-dir data/weekly/2026-W04

# Análise por fonte
news-scraper query \
  --dataset-dir data/weekly/2026-W04 \
  --sql "SELECT source, COUNT(*) as artigos, AVG(LENGTH(text)) as media_chars FROM articles GROUP BY source" \
  --format table

# Export para análise
news-scraper query \
  --dataset-dir data/weekly/2026-W04 \
  --sql "SELECT * FROM articles" \
  --format csv > data/weekly/2026-W04/export.csv
```

### 2. Monitoramento Diário Automatizado

```bash
#!/bin/bash
# Adicionar ao cron: 0 8 * * * /path/to/daily_collect.sh

TODAY=$(date +%Y-%m-%d)
OUTDIR="data/daily/$TODAY"

mkdir -p "$OUTDIR"

news-scraper collect \
  --source all \
  --limit 30 \
  --dataset-dir "$OUTDIR/articles" \
  --urls-out "$OUTDIR/urls.txt" \
  --use-proxy \
  --delay 2.0 \
  --verbose > "$OUTDIR/log.txt" 2>&1

# Relatório
news-scraper query \
  --dataset-dir "$OUTDIR/articles" \
  --sql "SELECT source, COUNT(*) as artigos FROM articles GROUP BY source" \
  --format csv > "$OUTDIR/report.csv"

echo "Coleta diária concluída: $TODAY" >> "$OUTDIR/summary.txt"
```

### 3. Teste e Validação

```bash
# Teste rápido sem scrape
news-scraper collect \
  --source infomoney \
  --limit 5 \
  --skip-scrape \
  --urls-out test_urls.txt

# Verificar URLs
cat test_urls.txt

# Scrape manual das URLs
news-scraper scrape \
  --input test_urls.txt \
  --dataset-dir data/test \
  --delay 1.0

# Validar resultado
news-scraper stats --dataset-dir data/test
```

---

## Dicas e Boas Práticas

### 🎯 Escolha de Fontes

- **InfoMoney**: Melhor cobertura de mercados financeiros BR
- **Money Times**: Foco em investimentos pessoais
- **Valor**: Jornal econômico tradicional e confiável
- **Bloomberg**: Perspectiva internacional
- **E-Investidor**: Educação financeira para investidores

### 🚀 Performance

- Use `--use-proxy` para evitar bloqueios por IP
- Ajuste `--delay` conforme necessário (2-5s é seguro)
- `--headless` sempre ativo para melhor performance
- Comece com `--limit` baixo para testes

### 📅 Filtros de Data

- `--start-date`/`--end-date` filtra **após** coleta
- Para histórico verdadeiro, use `historical generate`
- Formato ISO obrigatório: YYYY-MM-DD

### 💾 Armazenamento

- Dataset Parquet é particionado automaticamente
- Use `--urls-out` para backup antes do scrape
- `--skip-scrape` útil para validar URLs primeiro

### 🔍 Análise

- DuckDB permite SQL completo
- `format=csv` para exportar para Excel/Python
- `stats` dá overview rápido

### 🤖 Automação

- Scripts bash + cron para execução periódica
- Sempre use `--verbose` em produção
- Monitore logs e taxas de erro

---

## Troubleshooting

### Erro: "Nenhuma URL coletada"

- Verifique se a fonte está acessível
- Tente com `--use-proxy`
- Aumente `--limit`
- Use `--verbose` para ver detalhes

### Erro: "Proxy failed"

- Proxies gratuitos são instáveis (~30% sucesso)
- `--proxy-fallback` está ativo por padrão
- Sistema aprende quais proxies funcionam

### Erro: "Dataset not found"

- Crie o diretório: `mkdir -p data/processed/articles`
- Verifique o caminho com `--dataset-dir`

### Performance lenta

- Use `--headless` (padrão)
- Reduza `--limit` para testes
- Aumente `--delay` se houver rate limiting
- Considere `--use-proxy` para paralelização

---

## Referência Rápida

```bash
# Teste rápido
news-scraper collect --source infomoney --limit 5 --skip-scrape --urls-out test.txt

# Coleta completa
news-scraper collect --source all --limit 20 --use-proxy

# Com filtro de data
news-scraper collect --source all --limit 50 --start-date 2026-01-01 --end-date 2026-01-28

# Análise
news-scraper stats --dataset-dir data/processed/articles
news-scraper query --dataset-dir data/processed/articles --sql "SELECT COUNT(*) FROM articles"

# Ajuda
news-scraper --help
news-scraper collect --help
news-scraper query --help
```
