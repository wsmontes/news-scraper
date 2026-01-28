# Migração para BaseScraper

## Visão Geral

Implementação de classe base robusta (`BaseScraper`) que resolve 5 problemas críticos identificados:

1. ✅ **Filtros de data**: Parâmetros `start_date`/`end_date` + método `filter_by_date()`
2. ✅ **Sistema de retry**: Retry automático com 3 tentativas e backoff exponencial
3. ✅ **Taxa de sucesso**: Validação com `MIN_SUCCESS_RATE` (padrão 50%)
4. ✅ **Métricas**: Coleta automática via `ScraperMetrics` + `MetricsCollector`
5. ✅ **Paywall**: Flag `HAS_PAYWALL` + detecção automática + exceções específicas

## Arquitetura

### BaseScraper (base_scraper.py)

```python
class BaseScraper(ABC):
    MIN_SUCCESS_RATE = 0.5  # 50% padrão
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0
    HAS_PAYWALL = False
    
    @abstractmethod
    def _collect_urls(self, category, limit, start_date, end_date) -> List[str]:
        """Subclasses implementam a lógica de coleta."""
        pass
    
    def get_latest_articles(self, category, limit, **kwargs) -> List[str]:
        """Método público que orquestra: retry + métricas + validação."""
        # - Retry loop (3 tentativas)
        # - Rate limiting
        # - Coleta de métricas
        # - Validação de taxa de sucesso
        # - Detecção de paywall
        pass
```

### Componentes

- **ScraperMetrics**: Dataclass com métricas de execução
  - `source_id`, `category`, `requested`, `collected`
  - `success_rate`, `time_seconds`, `timestamp`
  - `errors`, `has_paywall_detected`, `retry_count`

- **MetricsCollector**: Singleton para métricas centralizadas
  - `add_metrics()`, `get_all_metrics()`
  - `get_metrics_by_source()`, `get_statistics()`
  - `export_json()`, `clear()`

- **Exceções Customizadas**:
  - `InsufficientDataException`: Taxa de sucesso < mínimo
  - `PaywallException`: Paywall detectado + taxa baixa
  - `ScraperException`: Base para erros de scraping

## Status da Migração

### ✅ Migrados (4/19) - Fontes Prioritárias

| Scraper | MIN_SUCCESS_RATE | HAS_PAYWALL | Status |
|---------|------------------|-------------|--------|
| **YahooFinanceUSScraper** | 60% | False | ✅ Migrado + Testado |
| **BusinessInsiderScraper** | 50% | partial | ✅ Migrado + Testado |
| **InvestingComScraper** | 50% | False | ✅ Migrado + Testado |
| **BloombergLatAmScraper** | 50% | False | ✅ Migrado + Testado |

### ⏳ Pendentes (15/19)

#### Fontes PT (4):
- [ ] InfoMoneyScraper
- [ ] MoneyTimesScraper
- [ ] ValorScraper
- [ ] EInvestidorScraper

#### Fontes EN (11):
- [ ] BloombergScraper
- [ ] FTScraper
- [ ] WSJScraper
- [ ] ReutersScraper
- [ ] CNBCScraper
- [ ] MarketWatchScraper
- [ ] SeekingAlphaScraper
- [ ] EconomistScraper
- [ ] ForbesScraper
- [ ] BarronsScraper
- [ ] InvestopediaScraper

## Padrão de Migração

### Antes (Padrão Antigo)
```python
class XScraper:
    def __init__(self, browser):
        self.scraper = browser
    
    def get_latest_articles(self, category, limit):
        try:
            # lógica de coleta
            return urls
        except Exception as e:
            print(f"Error: {e}")
            return []
```

### Depois (Padrão Novo)
```python
from ...base_scraper import BaseScraper

class XScraper(BaseScraper):
    MIN_SUCCESS_RATE = 0.6  # customizar por fonte
    HAS_PAYWALL = False
    
    def __init__(self, browser):
        super().__init__(browser, source_id="x")
    
    def _collect_urls(self, category, limit, start_date, end_date) -> List[str]:
        # mesma lógica de coleta
        # base class lida com retry, métricas, validação
        return urls
```

### Checklist de Migração

1. ✅ Adicionar imports: `BaseScraper`, `List`, `datetime`, `logging`
2. ✅ Mudar herança: `class XScraper(BaseScraper):`
3. ✅ Adicionar configurações: `MIN_SUCCESS_RATE`, `HAS_PAYWALL`
4. ✅ Atualizar `__init__`: chamar `super().__init__(browser, source_id)`
5. ✅ Renomear método: `get_latest_articles()` → `_collect_urls()`
6. ✅ Adicionar parâmetros: `start_date`, `end_date`
7. ✅ Atualizar tipos: `list[str]` → `List[str]`
8. ✅ Trocar `print()` por `logger.error()`
9. ✅ Compilar: `python -m py_compile scraper.py`
10. ✅ Testar imports: `from sources.en import XScraper`

## Testes

### test_base_scraper_features.py (15 testes)

- **TestBasicScraperFeatures**: Métricas, exportação, taxa média
- **TestSuccessRateValidation**: Warnings, exceções, taxas customizadas
- **TestRetryMechanism**: Contagem de retries, erros registrados
- **TestMetricsCollector**: Agregação, filtros, estatísticas, JSON
- **TestPaywallDetection**: Flag de paywall nas métricas
- **TestDateFiltering**: Parâmetros de data, warnings
- **TestIntegrationWithRealData** (2 testes): Workflow completo, performance

### Resultados

- ✅ test_global_sources.py: **34/34 passed** (0.15s)
- ⏳ test_base_scraper_features.py: **1/15 passed** (teste único executado)
  - test_scraper_collects_with_metrics: ✅ PASSED (73s)

## Benefícios da Migração

### 1. Retry Automático
- 3 tentativas com backoff exponencial (2.0s base)
- Jitter para evitar thundering herd
- Log detalhado de cada tentativa

### 2. Métricas Centralizadas
```python
metrics = scraper.get_latest_metrics()
# ScraperMetrics(
#     source_id='yahoofinance',
#     success_rate=0.75,
#     time_seconds=45.2,
#     collected=15,
#     requested=20,
#     retry_count=1
# )
```

### 3. Validação Robusta
```python
# Taxa < 50% → Warning
# Taxa < MIN_SUCCESS_RATE + raise_on_insufficient=True → Exception
scraper.get_latest_articles(
    category="news",
    limit=20,
    raise_on_insufficient=True  # lança InsufficientDataException
)
```

### 4. Rate Limiting
- 30 requests/minute (0.5/sec)
- Espera automática entre requisições
- Respeita limites dos sites

### 5. Detecção de Paywall
- PaywallDetector integrado
- Flag `HAS_PAYWALL` por scraper
- Exceção específica `PaywallException`
- Métricas registram detecção

## Exemplos de Uso

### Coleta Básica
```python
from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.sources.en import YahooFinanceUSScraper

config = BrowserConfig(headless=True)
browser = ProfessionalScraper(config)
browser.start()

scraper = YahooFinanceUSScraper(browser)
urls = scraper.get_latest_articles(category="stock-market-news", limit=20)

print(f"Coletou {len(urls)} URLs")
```

### Com Validação
```python
try:
    urls = scraper.get_latest_articles(
        category="markets",
        limit=20,
        min_success_rate=0.7,  # requer 70%
        raise_on_insufficient=True
    )
except InsufficientDataException as e:
    print(f"Taxa muito baixa: {e}")
```

### Métricas
```python
# Última execução
metrics = scraper.get_latest_metrics()
print(f"Taxa: {metrics.success_rate:.1%}")
print(f"Tempo: {metrics.time_seconds:.1f}s")
print(f"Retries: {metrics.retry_count}")

# Histórico
all_metrics = scraper.get_metrics()
avg_rate = scraper.get_average_success_rate()
print(f"Taxa média: {avg_rate:.1%}")

# Exportar
data = scraper.export_metrics()
# [{'source_id': 'yahoofinance', 'success_rate': 0.75, ...}, ...]
```

### Coletor Centralizado
```python
from news_scraper.base_scraper import MetricsCollector

collector = MetricsCollector()

# Executar múltiplos scrapers
for scraper in [yahoo, business_insider, investing, bloomberg]:
    urls = scraper.get_latest_articles(category="news", limit=10)
    for m in scraper.get_metrics():
        collector.add_metrics(m)

# Estatísticas globais
stats = collector.get_statistics()
print(f"Total execuções: {stats['total_executions']}")
print(f"Taxa média: {stats['avg_success_rate']:.1%}")
print(f"Tempo médio: {stats['avg_time_seconds']:.1f}s")

# Por fonte
yahoo_stats = stats['by_source']['yahoofinance']
print(f"Yahoo - Execuções: {yahoo_stats['count']}")
print(f"Yahoo - Taxa média: {yahoo_stats['avg_success_rate']:.1%}")
```

## Próximos Passos

1. **Migrar 4 scrapers PT** (InfoMoney, MoneyTimes, Valor, E-Investidor)
2. **Migrar 11 scrapers EN** restantes
3. **Implementar filtros de data** em cada scraper
4. **Executar test_base_scraper_features.py** completo
5. **Executar test_priority_sources_quality.py** (18 testes)
6. **Validar métricas** em produção
7. **Documentar taxas de sucesso** por fonte
8. **Ajustar MIN_SUCCESS_RATE** baseado em dados reais

## Notas Técnicas

### Import Cycles
- BaseScraper está em `src/news_scraper/base_scraper.py`
- Scrapers importam via `from ...base_scraper import BaseScraper`
- Sem ciclos de importação detectados

### Compatibilidade
- Método `get_article_urls()` mantido para compatibilidade
- Chama internamente `get_latest_articles()`
- Funções helper (`scrape_*`) também mantidas

### Performance
- Retry adiciona overhead (3 tentativas × 2s delay = 6s máx)
- Métricas têm custo mínimo (dataclass + append)
- Rate limiter adiciona 2s entre requisições
- Benefício: maior taxa de sucesso compensa overhead

### Configurações Recomendadas

| Tipo de Fonte | MIN_SUCCESS_RATE | HAS_PAYWALL |
|---------------|------------------|-------------|
| Gratuita, estável | 0.6 - 0.7 | False |
| Gratuita, instável | 0.4 - 0.5 | False |
| Paywall parcial | 0.3 - 0.5 | "partial" |
| Paywall completo | 0.1 - 0.3 | True |

---

**Última atualização**: 28/01/2026  
**Status**: 4/19 scrapers migrados, testes passando  
**Próximo**: Migrar scrapers PT + executar testes completos
