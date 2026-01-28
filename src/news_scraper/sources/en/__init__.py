"""
Fontes de notícias financeiras em Inglês (Global).

Inclui:
- Bloomberg (US)
- Financial Times (UK)
- Wall Street Journal (US)
- Reuters (UK)
- CNBC (US)
- MarketWatch (US)
- Seeking Alpha (US)
- The Economist (UK)
- Forbes (US)
- Barron's (US)
- Investopedia (US)
"""

from .bloomberg_scraper import BloombergScraper
from .bloomberg_latam_scraper import BloombergLatAmScraper
from .ft_scraper import FinancialTimesScraper
from .wsj_scraper import WSJScraper
from .reuters_scraper import ReutersScraper
from .cnbc_scraper import CNBCScraper
from .marketwatch_scraper import MarketWatchScraper
from .seekingalpha_scraper import SeekingAlphaScraper
from .economist_scraper import EconomistScraper
from .forbes_scraper import ForbesScraper
from .barrons_scraper import BarronsScraper
from .investopedia_scraper import InvestopediaScraper
from .yahoofinance_scraper import YahooFinanceUSScraper
from .businessinsider_scraper import BusinessInsiderScraper
from .investing_scraper import InvestingComScraper

__all__ = [
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
]
