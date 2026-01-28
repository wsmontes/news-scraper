# Revisão do CLI - News Scraper

## ✅ O que foi implementado

### 1. **Comando `collect` - Unificado e Completo**

Novo comando principal que resolve todos os problemas identificados:

```bash
news-scraper collect --source FONTE [OPTIONS]
```

#### Funcionalidades Principais:

**✓ Múltiplas Fontes:**
- Suporte a todas as 5 fontes: InfoMoney, Money Times, Valor, Bloomberg, E-Investidor
- Opção `--source all` para coletar de todas de uma vez
- Pode repetir `--source` para coletar de múltiplas fontes específicas

**✓ Filtros de Período:**
- `--start-date YYYY-MM-DD` - Filtrar artigos por data inicial
- `--end-date YYYY-MM-DD` - Filtrar artigos por data final
- Filtragem aplicada após coleta usando DuckDB

**✓ Controle de Fontes:**
- `--source infomoney|moneytimes|valor|bloomberg|einvestidor|all`
- `--category` - Categoria específica (varia por fonte)
- `--limit N` - Máximo de artigos por fonte

**✓ Sistema de Proxies:**
- `--use-proxy` - Ativa sistema inteligente de proxies
- `--proxy-fallback` - Fallback automático (padrão: ativo)
- Proxies aprendem qual funciona melhor para cada site

**✓ Configurações Avançadas:**
- `--headless` - Browser headless (padrão: ativo)
- `--delay N` - Delay entre requisições em segundos
- `--verbose` - Logs detalhados
- `--skip-scrape` - Apenas coletar URLs, não fazer scrape
- `--urls-out FILE` - Salvar URLs em arquivo texto

**✓ Saída:**
- `--dataset-dir` - Diretório do dataset Parquet (padrão: data/processed/articles)
- Particionamento automático por data

### 2. **Expansão do Comando `browser`**

Adicionados scrapers para todas as fontes:

```bash
news-scraper browser valor --category mercados --limit 20 --out urls.txt
news-scraper browser bloomberg --category economia --limit 15 --out urls.txt
news-scraper browser einvestidor --category mercados --limit 10 --out urls.txt
```

**Categorias por Fonte:**
- **Valor**: financas, empresas, mercados, mundo, politica, brasil
- **Bloomberg**: mercados, economia, negocios, tecnologia
- **E-Investidor**: mercados, investimentos, fundos-imobiliarios, cripto, acoes

### 3. **Documentação Completa**

**Arquivos Criados:**
- `docs/CLI_GUIDE.md` - Guia completo com todos os comandos
- `docs/CLI_EXAMPLES.sh` - Scripts de exemplo executáveis
- Exemplos práticos de workflows
- Troubleshooting e boas práticas

## 📋 Exemplos de Uso

### Caso 1: Coletar InfoMoney - últimas notícias

```bash
news-scraper collect --source infomoney --category mercados --limit 20
```

### Caso 2: Coletar múltiplas fontes

```bash
news-scraper collect \
  --source infomoney \
  --source moneytimes \
  --source valor \
  --limit 15
```

### Caso 3: Coletar todas as fontes

```bash
news-scraper collect --source all --limit 20
```

### Caso 4: Coletar com período específico

```bash
news-scraper collect \
  --source all \
  --limit 50 \
  --start-date 2026-01-01 \
  --end-date 2026-01-28
```

### Caso 5: Coletar com proxies

```bash
news-scraper collect \
  --source all \
  --limit 20 \
  --use-proxy \
  --verbose
```

### Caso 6: Apenas URLs (sem scrape)

```bash
news-scraper collect \
  --source bloomberg \
  --category mercados \
  --limit 30 \
  --skip-scrape \
  --urls-out data/raw/bloomberg_urls.txt
```

### Caso 7: Workflow completo

```bash
# Passo 1: Coletar
news-scraper collect \
  --source all \
  --category mercados \
  --limit 30 \
  --start-date 2026-01-20 \
  --end-date 2026-01-28 \
  --use-proxy \
  --delay 2.0 \
  --urls-out data/raw/urls.txt

# Passo 2: Estatísticas
news-scraper stats --dataset-dir data/processed/articles

# Passo 3: Consultar
news-scraper query \
  --dataset-dir data/processed/articles \
  --sql "SELECT source, COUNT(*) as total FROM articles GROUP BY source"
```

## 🎯 Todos os Parâmetros Necessários Implementados

### ✅ Controle de Fonte
- [x] Escolher fonte específica
- [x] Múltiplas fontes simultaneamente
- [x] Todas as fontes de uma vez
- [x] Categorias por fonte

### ✅ Controle de Período
- [x] Data inicial
- [x] Data final
- [x] Filtragem após coleta
- [x] Suporte a formato ISO (YYYY-MM-DD)

### ✅ Configurações de Scraping
- [x] Limite de artigos por fonte
- [x] Delay entre requisições
- [x] Browser headless
- [x] Modo verbose

### ✅ Sistema de Proxies
- [x] Ativar/desativar proxies
- [x] Fallback automático
- [x] Aprendizado por domínio
- [x] Estatísticas de sucesso

### ✅ Saída e Armazenamento
- [x] Dataset Parquet particionado
- [x] Arquivo de URLs (backup)
- [x] Skip scrape (apenas URLs)
- [x] Diretório customizado

### ✅ Análise e Consulta
- [x] SQL sobre dataset
- [x] Estatísticas
- [x] Filtros por data/fonte
- [x] Export CSV/JSON

## 📊 Comparação Antes vs Depois

### ANTES (Problemas):
- ❌ Sem filtro de período
- ❌ Sem suporte a proxies no CLI
- ❌ Valor, Bloomberg, E-Investidor sem CLI
- ❌ Sem comando unificado
- ❌ Sem coleta de múltiplas fontes
- ❌ Sem backup de URLs

### DEPOIS (Soluções):
- ✅ `--start-date` e `--end-date`
- ✅ `--use-proxy` e `--proxy-fallback`
- ✅ Todos os scrapers no CLI
- ✅ Comando `collect` unificado
- ✅ `--source` múltiplo ou `all`
- ✅ `--urls-out` para backup

## 🚀 Workflows Prontos para Produção

### 1. Monitoramento Diário

```bash
#!/bin/bash
# daily_collect.sh - Adicionar ao cron

TODAY=$(date +%Y-%m-%d)
news-scraper collect \
  --source all \
  --limit 30 \
  --dataset-dir "data/daily/$TODAY" \
  --use-proxy \
  --verbose
```

### 2. Análise Semanal

```bash
#!/bin/bash
# weekly_report.sh

news-scraper collect \
  --source all \
  --category mercados \
  --limit 50 \
  --start-date $(date -d "7 days ago" +%Y-%m-%d) \
  --end-date $(date +%Y-%m-%d) \
  --dataset-dir data/weekly

news-scraper stats --dataset-dir data/weekly
```

### 3. Teste e Validação

```bash
#!/bin/bash
# test_sources.sh

for source in infomoney moneytimes valor bloomberg einvestidor; do
  echo "Testando $source..."
  news-scraper collect \
    --source $source \
    --limit 3 \
    --skip-scrape \
    --urls-out "test_${source}.txt"
done
```

## 📝 Resumo

O CLI agora oferece **controle completo** sobre:

1. **Fontes**: Todas as 5 fontes + opção "all"
2. **Período**: Filtros de data inicial e final
3. **Proxies**: Sistema inteligente com aprendizado
4. **Configuração**: Delay, headless, verbose
5. **Saída**: Dataset Parquet + backup de URLs
6. **Análise**: SQL, stats, filtros

**Tudo que o usuário precisa para:**
- Coletar notícias de fontes específicas
- Definir período de interesse
- Usar proxies para evitar bloqueio
- Analisar dados coletados
- Automatizar coletas periódicas

## 🎯 Comando Mais Comum

```bash
# Caso de uso típico: coletar últimas notícias de todas as fontes
news-scraper collect --source all --limit 20 --use-proxy
```

**Pronto para produção!** ✅
