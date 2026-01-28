"""
CNBC Scraper - Business and financial news network.

Site: https://www.cnbc.com
Características:
- Livre
- Foco em mercados e investimentos
- Vídeos e artigos
- Alta frequência
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


class CNBCScraper(BaseScraper):
    """Scraper especializado para CNBC."""
    
    BASE_URL = "https://www.cnbc.com"
    MIN_SUCCESS_RATE = 0.6  # 60% - livre, estável
    HAS_PAYWALL = False
    
    CATEGORIES = {
        "markets": "https://www.cnbc.com/markets/",
        "investing": "https://www.cnbc.com/investing/",
        "business": "https://www.cnbc.com/business/",
        "technology": "https://www.cnbc.com/technology/",
        "economy": "https://www.cnbc.com/economy/",
        "finance": "https://www.cnbc.com/finance/",
    }
    
    SELECTORS = {
        "article_links": [
            "a.Card-title",
            "a.LatestNews-headline",
            "a[data-analytics='article-link']",
            "h3 a",
        ],
        "title": [
            "h1.ArticleHeader-headline",
            "h1.title",
        ],
        "text": [
            "div.ArticleBody-articleBody p",
            "div.group p",
        ],
        "date": [
            "time[data-testid='published-timestamp']",
            "time[datetime]",
        ],
        "author": [
            "a[data-testid='author-link']",
            "span.Author-authorName",
        ],
    }
    
    def __init__(self, scraper):
        """Inicializa o scraper."""
        super().__init__(scraper, source_id="cnbc")
    
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
            category: Categoria (markets, investing, business, etc.)
            limit: Número máximo de URLs
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        if not category:
            category = "markets"
            
        if category not in self.CATEGORIES:
            logger.error(f"Invalid category. Choose from: {list(self.CATEGORIES.keys())}")
            return []
        
        url = self.CATEGORIES[category]
        logger.info(f"Fetching CNBC articles from {category}: {url}")
        
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
                        if href and "cnbc.com" in href:
                            # Filtrar vídeos
                            if "/video/" not in href and "/live-tv/" not in href:
                                urls.add(href)
                                if len(urls) >= limit:
                                    break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
                
                if len(urls) >= limit:
                    break
            
            result = list(urls)[:limit]
            logger.info(f"Found {len(result)} CNBC articles")
            return result
        
        except Exception as e:
            logger.error(f"Error collecting CNBC URLs: {e}")
            return []
