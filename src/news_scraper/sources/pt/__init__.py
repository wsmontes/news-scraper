"""
Fontes de notícias financeiras em Português (Brasil).

Inclui:
- InfoMoney
- Money Times
- Valor Econômico
- E-Investidor
"""

from .infomoney_scraper import InfoMoneyScraper
from .moneytimes_scraper import MoneyTimesScraper
from .valor_scraper import ValorScraper
from .einvestidor_scraper import EInvestidorScraper

__all__ = [
    "InfoMoneyScraper",
    "MoneyTimesScraper",
    "ValorScraper",
    "EInvestidorScraper",
]
