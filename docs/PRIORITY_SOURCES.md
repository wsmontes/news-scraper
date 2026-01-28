# Seções Prioritárias de Notícias Financeiras

## 🎯 Objetivo

Este documento descreve as seções especializadas implementadas para capturar notícias financeiras de alta prioridade das principais fontes globais.

## 📰 Fontes e Seções Implementadas

### 1. Yahoo Finance US

**Scraper:** `YahooFinanceUSScraper`  
**Módulo:** `sources.en.yahoofinance_scraper`

#### Seções Prioritárias:
- **Stock Market News**: https://finance.yahoo.com/topic/stock-market-news/
  - Notícias do mercado de ações em tempo real
  - Análises de movimentos de mercado
  - Indicadores econômicos

- **Latest News**: https://finance.yahoo.com/topic/latest-news/
  - Últimas notícias financeiras
  - Breaking news do mercado
  - Updates em tempo real

#### Categorias Disponíveis:
```python
categories = {
    "stock-market-news": "Notícias do mercado de ações",
    "latest-news": "Últimas notícias",
    "markets": "Mercados em geral",
    "news": "Notícias gerais"
}
```

#### Uso:
```python
from news_scraper.sources.en import YahooFinanceUSScraper
from news_scraper.browser import BrowserScraper

browser = BrowserScraper()
scraper = YahooFinanceUSScraper(browser)

# Coletar notícias do mercado de ações
urls = scraper.get_latest_articles(category="stock-market-news", limit=20)

# Coletar últimas notícias
urls = scraper.get_latest_articles(category="latest-news", limit=20)
```

---

### 2. Business Insider

**Scraper:** `BusinessInsiderScraper`  
**Módulo:** `sources.en.businessinsider_scraper`

#### Seções Prioritárias:
- **Main**: https://www.businessinsider.com/
  - Principais notícias de negócios
  - Análises de mercado
  - Tendências empresariais

- **Markets**: https://markets.businessinsider.com/
  - Dados de mercado em tempo real
  - Análises de ações
  - Movimentos de commodities

#### Categorias Disponíveis:
```python
categories = {
    "main": "Site principal",
    "markets": "Mercados financeiros",
    "finance": "Finanças",
    "investing": "Investimentos",
    "stocks": "Ações",
    "news": "Notícias"
}
```

#### Uso:
```python
from news_scraper.sources.en import BusinessInsiderScraper
from news_scraper.browser import BrowserScraper

browser = BrowserScraper()
scraper = BusinessInsiderScraper(browser)

# Coletar do site principal
urls = scraper.get_latest_articles(category="main", limit=20)

# Coletar de markets
urls = scraper.get_latest_articles(category="markets", limit=20)
```

**⚠️ Nota:** Business Insider tem paywall parcial - alguns artigos são gratuitos.

---

### 3. Investing.com

**Scraper:** `InvestingComScraper`  
**Módulo:** `sources.en.investing_scraper`

#### Seção Prioritária:
- **News**: https://www.investing.com/news
  - Notícias de mercados globais
  - Análises econômicas
  - Dados de investimentos

#### Categorias Disponíveis:
```python
categories = {
    "news": "Notícias gerais",
    "stock-market-news": "Mercado de ações",
    "economy": "Economia",
    "cryptocurrency-news": "Criptomoedas",
    "commodities-news": "Commodities",
    "forex-news": "Forex"
}
```

#### Uso:
```python
from news_scraper.sources.en import InvestingComScraper
from news_scraper.browser import BrowserScraper

browser = BrowserScraper()
scraper = InvestingComScraper(browser)

# Coletar notícias gerais
urls = scraper.get_latest_articles(category="news", limit=20)

# Coletar notícias do mercado de ações
urls = scraper.get_latest_articles(category="stock-market-news", limit=20)
```

---

### 4. Bloomberg Latin America

**Scraper:** `BloombergLatAmScraper`  
**Módulo:** `sources.en.bloomberg_latam_scraper`

#### Seção Prioritária:
- **Latin America**: https://www.bloomberg.com/latinamerica
  - Notícias da América Latina
  - Economia regional
  - Mercados latino-americanos

#### Categorias Disponíveis:
```python
categories = {
    "latinamerica": "América Latina",
    "latin-america": "América Latina (alternativo)",
    "news": "Notícias",
    "markets": "Mercados"
}
```

#### Uso:
```python
from news_scraper.sources.en import BloombergLatAmScraper
from news_scraper.browser import BrowserScraper

browser = BrowserScraper()
scraper = BloombergLatAmScraper(browser)

# Coletar notícias da América Latina
urls = scraper.get_latest_articles(category="latinamerica", limit=20)
```

---

## 📊 Resumo das Fontes

| Fonte | ID | Seções | Paywall | Idioma |
|-------|-----|---------|---------|--------|
| **Yahoo Finance US** | `yahoofinance` | 4 | ❌ Não | EN |
| **Business Insider** | `businessinsider` | 6 | 🔐 Parcial | EN |
| **Investing.com** | `investing` | 6 | ❌ Não | EN |
| **Bloomberg Latin America** | `bloomberg-latam` | 4 | ❌ Não | EN |

**Total:** 4 fontes especializadas | 20 categorias combinadas

---

## 🚀 Uso via GlobalNewsManager

```python
from news_scraper.global_sources import GlobalNewsManager
from news_scraper.browser import BrowserScraper

# Criar browser
browser = BrowserScraper()

# Obter scraper via GlobalNewsManager
scraper = GlobalNewsManager.get_scraper("yahoofinance", browser)
urls = scraper.get_latest_articles(category="stock-market-news", limit=20)

# Informações da fonte
info = GlobalNewsManager.get_source_info("yahoofinance")
print(f"{info['name']} - {info['country']}")
print(f"Categorias: {', '.join(info['categories'])}")
```

---

## 🔧 Uso via CLI (Futuro)

```bash
# Yahoo Finance - Stock Market News
news-scraper collect --source yahoofinance --category stock-market-news --limit 20

# Business Insider - Markets
news-scraper collect --source businessinsider --category markets --limit 20

# Investing.com - News
news-scraper collect --source investing --category news --limit 20

# Bloomberg Latin America
news-scraper collect --source bloomberg-latam --category latinamerica --limit 20
```

---

## 📈 Estatísticas do Sistema

### Total de Fontes: **19**
- Fontes EN: **15** (78.9%)
- Fontes PT: **4** (21.1%)

### Por Tipo de Acesso:
- ✅ Gratuitas: **13** (68.4%)
- 🔐 Paywall Parcial: **2** (10.5%)
- 🔒 Paywall Completo: **4** (21.1%)

### Novas Fontes Adicionadas:
1. ✅ Yahoo Finance US (4 categorias)
2. ✅ Business Insider (6 categorias)
3. ✅ Investing.com (6 categorias)
4. ✅ Bloomberg Latin America (4 categorias)

---

## 🎯 Próximos Passos

1. ✅ Scrapers especializados criados
2. ✅ Integração com GlobalNewsManager
3. ⚠️ Testes unitários pendentes
4. ⚠️ Integração com CLI pendente
5. ⚠️ Benchmarks de performance pendentes

---

## 📝 Notas Técnicas

### Seletores CSS
Cada scraper possui seletores CSS otimizados para:
- Links de artigos
- Títulos
- Corpo do texto
- Datas de publicação

### Tratamento de Erros
- Validação de URLs
- Filtros para evitar páginas indesejadas
- Scroll automático para conteúdo dinâmico
- Timeouts configuráveis

### Performance
- Scroll inteligente: 5 scrolls com pausa de 3s
- Wait time: 5s para carregamento inicial
- Limite padrão: 20 URLs por coleta
- Caching automático (via tools.py)

### Anti-Bot
- User-Agent rotation (via tools.py)
- Rate limiting por domínio
- Delays aleatórios
- Headers realistas
