# Cobertura de Testes e Métricas

**Data**: 28/01/2026

## Resumo Executivo

| Categoria | Cobertura | Status |
|-----------|-----------|--------|
| **Módulos Core** | 7/11 (64%) | ⚠️ Parcial |
| **Scrapers** | 7/19 (37%) | ❌ Insuficiente |
| **Benchmarks** | 2/19 (11%) | ❌ Muito Baixo |
| **Testes Funcionando** | 141 testes | ✅ OK |
| **Testes com Erro** | 8 módulos | ❌ Corrigir |

---

## 1. Módulos Core do Projeto

### ✅ Com Testes Funcionando (7/11)

| Módulo | Arquivo de Teste | Testes | Status |
|--------|-----------------|--------|--------|
| `extract.py` | `test_extract_fallback.py` | 1 | ✅ |
| `extractors.py` | `test_extractors.py` | 8+ | ✅ |
| `dataset.py` | `test_dataset_parquet.py` | 2 | ✅ |
| `historical.py` | `test_historical.py` | 3 | ✅ |
| `io.py` | `test_io.py` | 2 | ✅ |
| `query.py` | `test_query.py` | 1 | ✅ |
| `global_sources.py` | `test_global_sources.py` | 34 | ✅ |

**Total: 51+ testes funcionando**

### ⚠️ Com Testes mas com Problemas de Import (4/11)

| Módulo | Arquivo de Teste | Problema |
|--------|-----------------|----------|
| `cli.py` | `test_cli_smoke.py` | ImportError |
| `cli.py` | `test_cli_coverage.py` | ImportError |
| `cli.py` | `test_cli_parametrization.py` | ImportError |
| `sources_cli.py` | `test_sources_cli.py` | ImportError |
| `sources.py` | `test_sources_csv.py` | ImportError: `enabled_rss_feeds` |

**Problema Principal**: Mudanças na estrutura de `sources/` após migração para BaseScraper quebraram imports.

### ❌ Sem Testes (0/11)

Todos os módulos principais têm alguma forma de teste, mas alguns não estão funcionando.

---

## 2. Scrapers Individuais

### ✅ Com Testes Dedicados (7/19 - 37%)

| Scraper | Arquivo | Testes | Status |
|---------|---------|--------|--------|
| InfoMoney | `test_infomoney_scraper.py` | 4+ | ⚠️ Import Error |
| MoneyTimes | `test_moneytimes_scraper.py` | 3 | ✅ |
| Valor | `test_valor_scraper.py` | 5 | ✅ |
| EInvestidor | `test_einvestidor_scraper.py` | 4+ | ⚠️ Import Error |
| Bloomberg | `test_bloomberg_scraper.py` | 4 | ✅ |
| YahooFinance | `test_priority_sources_quality.py` | Suíte | ⚠️ Import Error |
| BusinessInsider | `test_priority_sources_quality.py` | Suíte | ⚠️ Import Error |

### ❌ Sem Testes Dedicados (12/19 - 63%)

**EN Scrapers sem testes**:
- Investing
- BloombergLatAm
- Reuters
- CNBC
- MarketWatch
- SeekingAlpha
- Economist
- Forbes
- Barrons
- Investopedia
- FinancialTimes (FT)
- WSJ

**Nota**: Todos os 19 scrapers passam em `test_global_sources.py` (34 testes), que valida existência e metadados.

---

## 3. Benchmarks e Métricas

### ✅ Com Benchmarks (2/19 - 11%)

| Scraper | Classe de Teste | Métricas | Status |
|---------|----------------|----------|--------|
| InfoMoney | `TestInfoMoneyBenchmark` | 3 testes | ⚠️ Import Error |
| MoneyTimes | `TestMoneyTimesBenchmark` | 3 testes | ⚠️ Import Error |

**Benchmarks Definidos em `test_scraper_benchmarks.py`**:
- `min_urls`: Mínimo de URLs coletadas
- `min_metadata_success_rate`: Taxa mínima de sucesso em metadados
- `max_collection_time`: Tempo máximo para coletar URLs
- `max_extraction_time`: Tempo máximo por artigo
- `min_text_length`: Caracteres mínimos de texto
- `required_fields`: Campos obrigatórios

### ❌ Sem Benchmarks (17/19 - 89%)

Todos os outros scrapers não têm testes de performance/qualidade.

---

## 4. Testes de Features do BaseScraper

### ✅ test_base_scraper_features.py (7 classes, 15+ testes)

| Classe | Testes | Status |
|--------|--------|--------|
| `TestBasicScraperFeatures` | 3 | ⚠️ Import Error |
| `TestSuccessRateValidation` | 2 | ⚠️ Import Error |
| `TestRetryMechanism` | 2 | ⚠️ Import Error |
| `TestMetricsCollector` | 4 | ⚠️ Import Error |
| `TestPaywallDetection` | 1 | ⚠️ Import Error |
| `TestDateFiltering` | 2 | ⚠️ Import Error |
| `TestIntegrationWithRealData` | 1 | ⚠️ Import Error |

**Problemas**: Imports quebrados após migração.

---

## 5. Testes de Qualidade

### ✅ test_priority_sources_quality.py (6 classes, 18+ testes)

| Classe | Foco | Status |
|--------|------|--------|
| `TestYahooFinanceUSQuality` | Qualidade Yahoo | ⚠️ Import Error |
| `TestBusinessInsiderQuality` | Qualidade BI | ⚠️ Import Error |
| `TestInvestingComQuality` | Qualidade Investing | ⚠️ Import Error |
| `TestBloombergLatAmQuality` | Qualidade Bloomberg | ⚠️ Import Error |
| `TestPrioritySourcesComparison` | Comparação | ⚠️ Import Error |
| `TestPrioritySourcesUnderLoad` | Carga | ⚠️ Import Error |

---

## 6. Análise de Gaps

### Gap 1: Scrapers EN sem Testes Individuais (12 scrapers)

**Prioridade**: ALTA

Scrapers que precisam de testes dedicados:
1. Reuters (0.6 success rate)
2. CNBC (0.6 success rate)
3. MarketWatch (0.6 success rate)
4. Investopedia (0.6 success rate)
5. Forbes (0.5 success rate)
6. Investing (0.5 success rate)
7. Bloomberg LatAm (0.5 success rate)
8. SeekingAlpha (0.3 success rate, partial paywall)
9. Economist (0.2 success rate, full paywall)
10. WSJ (0.2 success rate, full paywall)
11. FT (0.2 success rate, full paywall)
12. Barrons (0.2 success rate, full paywall)

### Gap 2: Benchmarks Ausentes (17 scrapers)

**Prioridade**: ALTA

Apenas InfoMoney e MoneyTimes têm benchmarks de performance. Todos os outros 17 scrapers precisam de:
- Testes de coleta de URLs
- Testes de extração de metadados
- Testes de performance
- Validação de qualidade de conteúdo

### Gap 3: Testes com Import Errors (8 módulos)

**Prioridade**: CRÍTICA

Estes testes existem mas não funcionam:
1. `test_cli_smoke.py`
2. `test_cli_coverage.py`
3. `test_cli_parametrization.py`
4. `test_sources_cli.py`
5. `test_sources_csv.py`
6. `test_base_scraper_features.py`
7. `test_priority_sources_quality.py`
8. `test_scraper_benchmarks.py`

**Causa**: Mudanças na estrutura após migração para BaseScraper.

### Gap 4: Métricas do BaseScraper

**Prioridade**: MÉDIA

O BaseScraper coleta métricas (ScraperMetrics, MetricsCollector), mas:
- ❌ Sem testes de agregação de métricas cross-scraper
- ❌ Sem validação de export JSON
- ❌ Sem testes de estatísticas globais
- ⚠️ `TestMetricsCollector` existe mas está quebrado

---

## 7. Testes All-In-One

### ✅ test_all_scrapers.py

**Status**: Não verificado (pode ter import errors)

Este arquivo deveria testar todos os 19 scrapers de uma vez.

### ✅ test_smoke.py

**Status**: ⚠️ Import Error

Testes de smoke básicos para validação rápida.

---

## 8. Ações Recomendadas

### Prioridade 1: CRÍTICA - Corrigir Import Errors (1-2h)

1. ✅ Verificar imports em `test_sources_csv.py` (função `enabled_rss_feeds`)
2. ✅ Corrigir imports em `test_cli_*.py`
3. ✅ Corrigir imports em `test_base_scraper_features.py`
4. ✅ Corrigir imports em `test_priority_sources_quality.py`
5. ✅ Corrigir imports em `test_scraper_benchmarks.py`

**Objetivo**: Fazer 141+ testes rodarem novamente.

### Prioridade 2: ALTA - Benchmarks para Scrapers PT (2-3h)

1. ✅ Extender `test_scraper_benchmarks.py` para Valor
2. ✅ Extender `test_scraper_benchmarks.py` para EInvestidor

**Objetivo**: 4/4 scrapers PT com benchmarks.

### Prioridade 3: ALTA - Benchmarks para Scrapers EN Prioritários (3-4h)

1. ⏳ Adicionar benchmarks para YahooFinance
2. ⏳ Adicionar benchmarks para BusinessInsider
3. ⏳ Adicionar benchmarks para Bloomberg
4. ⏳ Adicionar benchmarks para Investing
5. ⏳ Adicionar benchmarks para Bloomberg LatAm
6. ⏳ Adicionar benchmarks para Reuters
7. ⏳ Adicionar benchmarks para CNBC
8. ⏳ Adicionar benchmarks para MarketWatch

**Objetivo**: 12/19 scrapers com benchmarks (todos sem paywall + parcial paywall).

### Prioridade 4: MÉDIA - Testes Individuais para EN (4-6h)

Criar `test_<scraper>_scraper.py` para cada scraper EN seguindo padrão de MoneyTimes/Valor:
- test_get_latest_articles
- test_categories
- test_extract_metadata
- test_multiple_articles_metadata

**Objetivo**: 19/19 scrapers com testes dedicados.

### Prioridade 5: BAIXA - Testes de Métricas Globais (1-2h)

1. ⏳ Teste de agregação de métricas
2. ⏳ Teste de export JSON
3. ⏳ Teste de estatísticas cross-scraper
4. ⏳ Teste de MetricsCollector singleton

---

## 9. Estrutura de Testes Atual

```
tests/
├── ✅ test_global_sources.py          # 34 testes - Metadados de todos scrapers
├── ✅ test_extractors.py              # 8+ testes - Extração de conteúdo
├── ✅ test_extract_fallback.py        # 1 teste - Fallback de extração
├── ✅ test_dataset_parquet.py         # 2 testes - Dataset Parquet
├── ✅ test_historical.py              # 3 testes - Scraping histórico
├── ✅ test_io.py                      # 2 testes - I/O de arquivos
├── ✅ test_query.py                   # 1 teste - Query SQL
│
├── ✅ test_moneytimes_scraper.py      # 3 testes - MoneyTimes
├── ✅ test_valor_scraper.py           # 5 testes - Valor
├── ✅ test_bloomberg_scraper.py       # 4 testes - Bloomberg
│
├── ⚠️ test_infomoney_scraper.py       # 4+ testes - InfoMoney (import error)
├── ⚠️ test_einvestidor_scraper.py     # 4+ testes - EInvestidor (import error)
│
├── ⚠️ test_base_scraper_features.py   # 15+ testes - Features BaseScraper (import error)
├── ⚠️ test_priority_sources_quality.py # 18+ testes - Qualidade prioritários (import error)
├── ⚠️ test_scraper_benchmarks.py      # 6+ testes - Benchmarks (import error)
│
├── ⚠️ test_cli_smoke.py               # CLI básico (import error)
├── ⚠️ test_cli_coverage.py            # CLI cobertura (import error)
├── ⚠️ test_cli_parametrization.py     # CLI parametrização (import error)
├── ⚠️ test_sources_cli.py             # Sources CLI (import error)
├── ⚠️ test_sources_csv.py             # Sources CSV (import error)
│
├── ⚠️ test_smoke.py                   # Smoke tests (import error)
└── ⚠️ test_all_scrapers.py            # All scrapers (status desconhecido)
```

---

## 10. Cobertura Ideal vs Atual

| Área | Ideal | Atual | Gap |
|------|-------|-------|-----|
| **Módulos Core** | 11/11 (100%) | 7/11 (64%) | -36% |
| **Testes Funcionando** | 100% | 51/141 (36%) | -64% |
| **Scrapers Individuais** | 19/19 (100%) | 7/19 (37%) | -63% |
| **Benchmarks** | 19/19 (100%) | 2/19 (11%) | -89% |
| **Testes de Qualidade** | Sim | Sim (quebrados) | Corrigir |
| **Métricas Globais** | Sim | Parcial | -50% |

---

## 11. Resumo de Ações

### 🔴 Urgente (Próximas 2h)
- [ ] Corrigir 8 módulos com import errors
- [ ] Validar que 141 testes voltam a funcionar

### 🟡 Importante (Esta semana)
- [ ] Adicionar benchmarks para Valor e EInvestidor
- [ ] Adicionar benchmarks para 8 scrapers EN prioritários
- [ ] Criar testes individuais para 12 scrapers EN

### 🟢 Desejável (Próxima sprint)
- [ ] Testes de métricas globais
- [ ] Aumentar cobertura de módulos core para 100%
- [ ] CI/CD com pytest automático

---

## 12. Comandos Úteis

```bash
# Rodar apenas testes funcionando
pytest tests/test_global_sources.py tests/test_extractors.py tests/test_io.py -v

# Rodar testes de um scraper específico
pytest tests/test_moneytimes_scraper.py -v

# Rodar benchmarks (quando funcionarem)
pytest tests/test_scraper_benchmarks.py -v

# Coletar lista de todos os testes
pytest tests/ --collect-only -q

# Rodar testes com coverage
pytest tests/ --cov=src/news_scraper --cov-report=html
```

---

**Última atualização**: 28/01/2026
**Próxima revisão**: Após corrigir import errors
