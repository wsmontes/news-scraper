# Organização das Fontes de Notícias

## Estrutura de Diretórios

O sistema de scraping está organizado por idioma para facilitar manutenção e expansão:

```
src/news_scraper/
├── sources/
│   ├── __init__.py          # Agrega todos os scrapers
│   ├── pt/                  # Fontes em Português (Brasil)
│   │   ├── __init__.py      # Exporta scrapers PT
│   │   ├── infomoney_scraper.py
│   │   ├── moneytimes_scraper.py
│   │   ├── valor_scraper.py
│   │   └── einvestidor_scraper.py
│   └── en/                  # Fontes em Inglês (Global)
│       ├── __init__.py      # Exporta scrapers EN
│       ├── bloomberg_scraper.py
│       ├── ft_scraper.py
│       ├── wsj_scraper.py
│       ├── reuters_scraper.py
│       ├── cnbc_scraper.py
│       ├── marketwatch_scraper.py
│       ├── seekingalpha_scraper.py
│       ├── economist_scraper.py
│       ├── forbes_scraper.py
│       ├── barrons_scraper.py
│       └── investopedia_scraper.py
└── global_sources.py        # Gerenciador central
```

## Fontes Disponíveis

### Fontes Brasileiras (PT) - 4 fontes

| Fonte | País | Paywall | Categorias |
|-------|------|---------|------------|
| **InfoMoney** | BR | ❌ | mercados, economia, politica, negocios |
| **Money Times** | BR | ❌ | mercado, investimentos, economia |
| **Valor Econômico** | BR | ✅ | financas, empresas, mercados, mundo, politica, brasil |
| **E-Investidor** | BR | ❌ | mercados, investimentos, fundos-imobiliarios, cripto, acoes |

### Fontes Globais (EN) - 11 fontes

| Fonte | País | Paywall | Categorias |
|-------|------|---------|------------|
| **Bloomberg** | US | ❌ | markets, economics, industries, technology, politics |
| **Financial Times** | UK | ✅ | markets, companies, technology, opinion, world, economics |
| **Wall Street Journal** | US | ✅ | markets, economy, business, tech, finance, world |
| **Reuters** | UK | ❌ | markets, business, technology, world, breakingviews |
| **CNBC** | US | ❌ | markets, investing, business, technology, economy, finance |
| **MarketWatch** | US | ❌ | latest, markets, investing, personal-finance, economy-politics |
| **Seeking Alpha** | US | 🔐 | market-news, top-news, wall-street-breakfast, etfs, analysis |
| **The Economist** | UK | ✅ | finance, business, briefing, leaders, world |
| **Forbes** | US | ❌ | investing, markets, business, money, crypto |
| **Barron's** | US | ✅ | market-news, stocks, investing, advisor, features |
| **Investopedia** | US | ❌ | markets, investing, stocks, economy, personal-finance |

**Legenda:**
- ❌ = Sem paywall (gratuito)
- ✅ = Com paywall (requer assinatura)
- 🔐 = Paywall parcial (alguns artigos gratuitos)

## Estatísticas

- **Total:** 15 fontes
- **Português:** 4 fontes (26.7%)
- **Inglês:** 11 fontes (73.3%)
- **Gratuitas:** 10 fontes (66.7%)
- **Com Paywall:** 4 fontes (26.7%)
- **Paywall Parcial:** 1 fonte (6.7%)

## Como Usar

### Importação Direta

```python
# Importar scraper específico PT
from news_scraper.sources.pt import InfoMoneyScraper

# Importar scraper específico EN
from news_scraper.sources.en import BloombergScraper

# Importar todos
from news_scraper.sources import (
    InfoMoneyScraper,
    BloombergScraper,
    # ... etc
)
```

### Usando o GlobalNewsManager

```python
from news_scraper.global_sources import GlobalNewsManager

# Listar fontes por idioma
pt_sources = GlobalNewsManager.list_sources(language='pt')
en_sources = GlobalNewsManager.list_sources(language='en')

# Listar apenas fontes gratuitas
free_sources = GlobalNewsManager.list_sources(no_paywall=True)

# Obter informações de uma fonte
info = GlobalNewsManager.get_source_info('bloomberg')
print(f"{info['name']} - {info['country']} - {info['language']}")

# Obter scraper (precisa de browser_scraper)
from news_scraper.browser import BrowserScraper
browser = BrowserScraper()
scraper = GlobalNewsManager.get_scraper('infomoney', browser)
```

### Via CLI

```bash
# Coletar de fonte PT
news-scraper collect --source infomoney --category mercados

# Coletar de fonte EN
news-scraper collect --source bloomberg --category markets

# Listar todas as fontes
news-scraper sources list

# Ver informações de uma fonte
news-scraper sources info infomoney
```

## Vantagens da Organização

1. **Clareza:** Fácil identificar o idioma da fonte
2. **Manutenção:** Mudanças em um idioma não afetam o outro
3. **Escalabilidade:** Fácil adicionar novos idiomas (es/, fr/, etc.)
4. **Imports Limpos:** Estrutura clara de importações
5. **Testes Organizados:** Testes podem ser organizados por idioma

## Expansão Futura

Para adicionar novas fontes:

1. **Criar o scraper:**
   ```
   src/news_scraper/sources/{idioma}/{nome}_scraper.py
   ```

2. **Adicionar ao __init__.py do idioma:**
   ```python
   from .novo_scraper import NovoScraper
   __all__ = [..., "NovoScraper"]
   ```

3. **Adicionar ao __init__.py principal:**
   ```python
   from .{idioma} import NovoScraper
   __all__ = [..., "NovoScraper"]
   ```

4. **Registrar no GlobalNewsManager:**
   ```python
   SOURCES = {
       "novo": {
           "name": "Novo Site",
           "country": "XX",
           "language": "xx",
           "paywall": False,
           "categories": [...],
           "module": "sources.xx.novo_scraper",
           "class": "NovoScraper",
       }
   }
   ```

Para adicionar novo idioma:

1. **Criar diretório:**
   ```bash
   mkdir src/news_scraper/sources/{idioma}
   ```

2. **Criar __init__.py:**
   ```python
   from .scraper1 import Scraper1
   from .scraper2 import Scraper2
   __all__ = ["Scraper1", "Scraper2"]
   ```

3. **Atualizar sources/__init__.py:**
   ```python
   from .{idioma} import Scraper1, Scraper2
   ```
