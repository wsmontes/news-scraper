"""Smoke test rápido para verificar se todos os scrapers conseguem coletar URLs."""

from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.sources.pt import (
    InfoMoneyScraper,
    ValorScraper,
    EInvestidorScraper,
    MoneyTimesScraper,
)
from news_scraper.sources.en import BloombergScraper


def test_all_sources_quick():
    """Teste rápido de todas as fontes."""
    config = BrowserConfig(headless=True)
    
    with ProfessionalScraper(config) as scraper:
        sources = [
            ("InfoMoney", InfoMoneyScraper),
            ("MoneyTimes", MoneyTimesScraper),
            ("Valor", ValorScraper),
            ("Bloomberg", BloombergScraper),
            ("E-Investidor", EInvestidorScraper),
        ]
        
        results = []
        
        for name, scraper_class in sources:
            try:
                s = scraper_class(scraper)
                urls = s.get_latest_articles(limit=2)
                status = "✅" if len(urls) > 0 else "❌"
                results.append((name, status, len(urls)))
                print(f"{status} {name}: {len(urls)} URLs")
            except Exception as e:
                results.append((name, "❌", 0))
                print(f"❌ {name}: {str(e)[:50]}")
        
        print("\nRESUMO:")
        for name, status, count in results:
            print(f"{status} {name}: {count} URLs")


if __name__ == "__main__":
    test_all_sources_quick()
