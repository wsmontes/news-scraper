"""
Investopedia Scraper - Financial education and news.

Site: https://www.investopedia.com
Características:
- Livre
- Foco educacional
- Notícias + tutoriais
- Análises de mercado
"""

from __future__ import annotations

import logging
from typing import Optional, List
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class InvestopediaScraper(BaseScraper):
    """Scraper especializado para Investopedia."""
    
    MIN_SUCCESS_RATE = 0.6
    HAS_PAYWALL = False
    
    CATEGORIES = {
        "markets": "https://www.investopedia.com/markets-news-4427704",
        "investing": "https://www.investopedia.com/investing-4427760",
        "stocks": "https://www.investopedia.com/stocks-4427785",
        "economy": "https://www.investopedia.com/economy-4689800",
        "personal-finance": "https://www.investopedia.com/personal-finance-4427760",
    }
    
    SELECTORS = {
        "article_links": [
            "a.card-title",
            "a.comp.mntl-card-list-items",
            "h3 a",
        ],
        "title": [
            "h1#article-heading",
            "h1.article-heading",
        ],
        "text": [
            "div#article-body p",
            "div.article-body-content p",
        ],
        "date": [
            "time[datetime]",
            "span.article-publish-date",
        ],
        "author": [
            "a.mntl-attribution__item-name",
            "span.article-byline-author",
        ],
    }
    
    def __init__(self, scraper):
        """Inicializa o scraper."""
        super().__init__(scraper, source_id="investopedia")
    
    def _collect_urls(
        self,
        category: Optional[str] = None,
        limit: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[str]:
        """
        Implementação da coleta de URLs (método abstrato da classe base).
        
        Args:
            category: Categoria (markets, investing, stocks, etc.)
            limit: Número máximo de URLs
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        if not category:
            category = "markets"
            
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category. Choose from: {list(self.CATEGORIES.keys())}")
        
        url = self.CATEGORIES[category]
        logger.info(f"Fetching Investopedia articles from {category}: {url}")
        
        driver = self.scraper.driver
        
        try:
            driver.get(url)
            
            # Esperar carregar
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Scroll
            self.scraper._scroll_page(driver, scroll_times=2)
            
            # Coletar links
            urls = set()
            for selector in self.SELECTORS["article_links"]:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        href = elem.get_attribute("href")
                        if href and "investopedia.com" in href:
                            # Filtrar páginas especiais (tutoriais, termos, etc)
                            if "/terms/" not in href and "/what-is" not in href.lower():
                                urls.add(href)
                                if len(urls) >= limit:
                                    break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
                
                if len(urls) >= limit:
                    break
            
            result = list(urls)[:limit]
            logger.info(f"Found {len(result)} Investopedia articles")
            return result
        
        except Exception as e:
            logger.error(f"Error fetching Investopedia articles: {e}")
            return []
