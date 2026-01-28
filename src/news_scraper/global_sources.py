"""
Global News Sources Manager - Gerenciamento centralizado de todas as fontes.

Inclui 14 fontes de notícias financeiras:
- Globais: Bloomberg, FT, WSJ, Reuters, CNBC, MarketWatch, Seeking Alpha, 
          The Economist, Forbes, Barron's, Investopedia
- Brasil: InfoMoney, Money Times, Valor Econômico, E-Investidor
"""

from __future__ import annotations

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class GlobalNewsManager:
    """Gerenciador central de todas as fontes de notícias."""
    
    # Metadados de todas as fontes
    SOURCES = {
        # FONTES GLOBAIS (EN)
        "bloomberg": {
            "name": "Bloomberg",
            "country": "US",
            "language": "en",
            "paywall": False,
            "categories": ["markets", "economics", "industries", "technology", "politics"],
            "module": "sources.en.bloomberg_scraper",
            "class": "BloombergScraper",
        },
        "ft": {
            "name": "Financial Times",
            "country": "UK",
            "language": "en",
            "paywall": True,
            "categories": ["markets", "companies", "technology", "opinion", "world", "economics"],
            "module": "sources.en.ft_scraper",
            "class": "FinancialTimesScraper",
        },
        "wsj": {
            "name": "Wall Street Journal",
            "country": "US",
            "language": "en",
            "paywall": True,
            "categories": ["markets", "economy", "business", "tech", "finance", "world"],
            "module": "sources.en.wsj_scraper",
            "class": "WSJScraper",
        },
        "reuters": {
            "name": "Reuters",
            "country": "UK",
            "language": "en",
            "paywall": False,
            "categories": ["markets", "business", "technology", "world", "breakingviews"],
            "module": "sources.en.reuters_scraper",
            "class": "ReutersScraper",
        },
        "cnbc": {
            "name": "CNBC",
            "country": "US",
            "language": "en",
            "paywall": False,
            "categories": ["markets", "investing", "business", "technology", "economy", "finance"],
            "module": "sources.en.cnbc_scraper",
            "class": "CNBCScraper",
        },
        "marketwatch": {
            "name": "MarketWatch",
            "country": "US",
            "language": "en",
            "paywall": False,
            "categories": ["latest", "markets", "investing", "personal-finance", "economy-politics"],
            "module": "sources.en.marketwatch_scraper",
            "class": "MarketWatchScraper",
        },
        "seekingalpha": {
            "name": "Seeking Alpha",
            "country": "US",
            "language": "en",
            "paywall": "partial",
            "categories": ["market-news", "top-news", "wall-street-breakfast", "etfs", "analysis"],
            "module": "sources.en.seekingalpha_scraper",
            "class": "SeekingAlphaScraper",
        },
        "economist": {
            "name": "The Economist",
            "country": "UK",
            "language": "en",
            "paywall": True,
            "categories": ["finance", "business", "briefing", "leaders", "world"],
            "module": "sources.en.economist_scraper",
            "class": "EconomistScraper",
        },
        "forbes": {
            "name": "Forbes",
            "country": "US",
            "language": "en",
            "paywall": False,
            "categories": ["investing", "markets", "business", "money", "crypto"],
            "module": "sources.en.forbes_scraper",
            "class": "ForbesScraper",
        },
        "barrons": {
            "name": "Barron's",
            "country": "US",
            "language": "en",
            "paywall": True,
            "categories": ["market-news", "stocks", "investing", "advisor", "features"],
            "module": "sources.en.barrons_scraper",
            "class": "BarronsScraper",
        },
        "investopedia": {
            "name": "Investopedia",
            "country": "US",
            "language": "en",
            "paywall": False,
            "categories": ["markets", "investing", "stocks", "economy", "personal-finance"],
            "module": "sources.en.investopedia_scraper",
            "class": "InvestopediaScraper",
        },
        "yahoofinance": {
            "name": "Yahoo Finance US",
            "country": "US",
            "language": "en",
            "paywall": False,
            "categories": ["stock-market-news", "latest-news", "markets", "news"],
            "module": "sources.en.yahoofinance_scraper",
            "class": "YahooFinanceUSScraper",
        },
        "businessinsider": {
            "name": "Business Insider",
            "country": "US",
            "language": "en",
            "paywall": "partial",
            "categories": ["main", "markets", "finance", "investing", "stocks", "news"],
            "module": "sources.en.businessinsider_scraper",
            "class": "BusinessInsiderScraper",
        },
        "investing": {
            "name": "Investing.com",
            "country": "US",
            "language": "en",
            "paywall": False,
            "categories": ["news", "stock-market-news", "economy", "cryptocurrency-news", "commodities-news", "forex-news"],
            "module": "sources.en.investing_scraper",
            "class": "InvestingComScraper",
        },
        "bloomberg-latam": {
            "name": "Bloomberg Latin America",
            "country": "US",
            "language": "en",
            "paywall": False,
            "categories": ["latinamerica", "latin-america", "news", "markets"],
            "module": "sources.en.bloomberg_latam_scraper",
            "class": "BloombergLatAmScraper",
        },
        
        # FONTES BRASILEIRAS (PT)
        "infomoney": {
            "name": "InfoMoney",
            "country": "BR",
            "language": "pt",
            "paywall": False,
            "categories": ["mercados", "economia", "politica", "negocios"],
            "module": "sources.pt.infomoney_scraper",
            "class": "InfoMoneyScraper",
        },
        "moneytimes": {
            "name": "Money Times",
            "country": "BR",
            "language": "pt",
            "paywall": False,
            "categories": ["mercado", "investimentos", "economia"],
            "module": "sources.pt.moneytimes_scraper",
            "class": "MoneyTimesScraper",
        },
        "valor": {
            "name": "Valor Econômico",
            "country": "BR",
            "language": "pt",
            "paywall": True,
            "categories": ["financas", "empresas", "mercados", "mundo", "politica", "brasil"],
            "module": "sources.pt.valor_scraper",
            "class": "ValorScraper",
        },
        "einvestidor": {
            "name": "E-Investidor",
            "country": "BR",
            "language": "pt",
            "paywall": False,
            "categories": ["mercados", "investimentos", "fundos-imobiliarios", "cripto", "acoes"],
            "module": "sources.pt.einvestidor_scraper",
            "class": "EInvestidorScraper",
        },
    }
    
    @classmethod
    def get_source_info(cls, source_id: str) -> Optional[dict]:
        """Retorna informações sobre uma fonte."""
        return cls.SOURCES.get(source_id)
    
    @classmethod
    def list_sources(cls, country: str = None, language: str = None, no_paywall: bool = False) -> list[str]:
        """
        Lista fontes disponíveis com filtros opcionais.
        
        Args:
            country: Filtrar por país (US, UK, BR)
            language: Filtrar por idioma (en, pt)
            no_paywall: Apenas fontes sem paywall
            
        Returns:
            Lista de IDs de fontes
        """
        sources = []
        for source_id, info in cls.SOURCES.items():
            if country and info["country"] != country:
                continue
            if language and info["language"] != language:
                continue
            if no_paywall and info["paywall"] is True:
                continue
            sources.append(source_id)
        
        return sources
    
    @classmethod
    def get_scraper(cls, source_id: str, browser_scraper):
        """
        Instancia o scraper apropriado para a fonte.
        
        Args:
            source_id: ID da fonte
            browser_scraper: Instância do browser scraper
            
        Returns:
            Instância do scraper especializado
        """
        info = cls.get_source_info(source_id)
        if not info:
            raise ValueError(f"Unknown source: {source_id}")
        
        # Importar dinamicamente
        module_name = info["module"]
        class_name = info["class"]
        
        try:
            module = __import__(f"news_scraper.{module_name}", fromlist=[class_name])
            scraper_class = getattr(module, class_name)
            return scraper_class(browser_scraper)
        except ImportError as e:
            logger.error(f"Failed to import {module_name}: {e}")
            raise
        except AttributeError as e:
            logger.error(f"Class {class_name} not found in {module_name}: {e}")
            raise
    
    @classmethod
    def print_sources_table(cls):
        """Imprime tabela formatada de todas as fontes."""
        print("\n" + "="*80)
        print("FONTES DE NOTÍCIAS FINANCEIRAS DISPONÍVEIS")
        print("="*80)
        
        # Agrupar por país
        by_country = {}
        for source_id, info in cls.SOURCES.items():
            country = info["country"]
            if country not in by_country:
                by_country[country] = []
            by_country[country].append((source_id, info))
        
        for country in ["US", "UK", "BR"]:
            if country not in by_country:
                continue
            
            country_names = {"US": "Estados Unidos", "UK": "Reino Unido", "BR": "Brasil"}
            print(f"\n📍 {country_names[country]} ({country})")
            print("-" * 80)
            
            for source_id, info in sorted(by_country[country], key=lambda x: x[1]["name"]):
                paywall_icon = "🔒" if info["paywall"] is True else "🔓"
                if info["paywall"] == "partial":
                    paywall_icon = "🔐"
                
                categories_str = ", ".join(info["categories"][:3])
                if len(info["categories"]) > 3:
                    categories_str += f" (+{len(info['categories'])-3})"
                
                print(f"  {paywall_icon} {source_id:15} - {info['name']:25} | {categories_str}")
        
        print("\n" + "="*80)
        print(f"Total: {len(cls.SOURCES)} fontes")
        print("🔓 Livre  🔐 Parcial  🔒 Paywall")
        print("="*80 + "\n")
    
    @classmethod
    def get_global_sources(cls) -> list[str]:
        """Retorna lista de fontes globais (inglês)."""
        return cls.list_sources(language="en")
    
    @classmethod
    def get_brazilian_sources(cls) -> list[str]:
        """Retorna lista de fontes brasileiras."""
        return cls.list_sources(country="BR")
    
    @classmethod
    def get_free_sources(cls) -> list[str]:
        """Retorna lista de fontes sem paywall."""
        return cls.list_sources(no_paywall=True)


def collect_from_source(source_id: str, category: str = None, limit: int = 20, use_proxy: bool = False) -> list[str]:
    """
    Função auxiliar para coletar URLs de uma fonte.
    
    Args:
        source_id: ID da fonte
        category: Categoria (opcional, usa primeira se não especificada)
        limit: Máximo de URLs
        use_proxy: Usar proxy
        
    Returns:
        Lista de URLs
    """
    from .browser import ProfessionalScraper, BrowserConfig
    
    # Configurar browser
    config = BrowserConfig(
        headless=True,
        use_proxy=use_proxy,
    )
    browser = ProfessionalScraper(config)
    
    # Obter scraper
    scraper = GlobalNewsManager.get_scraper(source_id, browser)
    
    # Determinar categoria
    if category is None:
        source_info = GlobalNewsManager.get_source_info(source_id)
        category = source_info["categories"][0]  # Primeira categoria
    
    # Coletar
    logger.info(f"Collecting from {source_id} - category: {category}, limit: {limit}")
    urls = scraper.get_latest_articles(category=category, limit=limit)
    
    return urls


if __name__ == "__main__":
    # Teste rápido
    GlobalNewsManager.print_sources_table()
    
    print("\nFontes globais (inglês):", len(GlobalNewsManager.get_global_sources()))
    print("Fontes brasileiras:", len(GlobalNewsManager.get_brazilian_sources()))
    print("Fontes livres:", len(GlobalNewsManager.get_free_sources()))
