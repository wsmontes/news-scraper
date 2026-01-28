"""
Módulo de fontes de notícias financeiras.

Organizado por idioma:
- pt: Fontes em Português (Brasil)
- en: Fontes em Inglês (Global)
"""

# Importar scrapers brasileiros
from .pt import (
    InfoMoneyScraper,
    MoneyTimesScraper,
    ValorScraper,
    EInvestidorScraper,
)

# Importar scrapers globais
from .en import (
    BloombergScraper,
    BloombergLatAmScraper,
    FinancialTimesScraper,
    WSJScraper,
    ReutersScraper,
    CNBCScraper,
    MarketWatchScraper,
    SeekingAlphaScraper,
    EconomistScraper,
    ForbesScraper,
    BarronsScraper,
    InvestopediaScraper,
    YahooFinanceUSScraper,
    BusinessInsiderScraper,
    InvestingComScraper,
)

# Importar funções utilitárias CSV
from .csv_utils import load_sources_csv, enabled_rss_feeds, Source

__all__ = [
    # Português (Brasil)
    "InfoMoneyScraper",
    "MoneyTimesScraper",
    "ValorScraper",
    "EInvestidorScraper",
    # Inglês (Global)
    "BloombergScraper",
    "BloombergLatAmScraper",
    "FinancialTimesScraper",
    "WSJScraper",
    "ReutersScraper",
    "CNBCScraper",
    "MarketWatchScraper",
    "SeekingAlphaScraper",
    "EconomistScraper",
    "ForbesScraper",
    "BarronsScraper",
    "InvestopediaScraper",
    "YahooFinanceUSScraper",
    "BusinessInsiderScraper",
    "InvestingComScraper",
    # CSV Utils
    "load_sources_csv",
    "enabled_rss_feeds",
    "Source",
]
