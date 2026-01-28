"""
News Scraper - Sistema profissional de scraping de notícias financeiras.

Scrapers especializados para as principais fontes brasileiras:
- InfoMoney
- Valor Econômico
- Bloomberg Brasil
- E-Investidor (Estadão)
- Money Times
"""

__all__ = [
    "__version__",
    "InfoMoneyScraper",
    "ValorScraper",
    "BloombergScraper",
    "EInvestidorScraper",
    "MoneyTimesScraper",
]

__version__ = "0.1.0"

# Importações para conveniência
from news_scraper.infomoney_scraper import InfoMoneyScraper
from news_scraper.valor_scraper import ValorScraper
from news_scraper.bloomberg_scraper import BloombergScraper
from news_scraper.einvestidor_scraper import EInvestidorScraper
from news_scraper.moneytimes_scraper import MoneyTimesScraper
