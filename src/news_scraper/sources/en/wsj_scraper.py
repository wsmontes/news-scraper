"""
Wall Street Journal (WSJ) Scraper - Premier business news.

Site: https://www.wsj.com
Características:
- Paywall
- Alto padrão jornalístico
- Categorias: markets, economy, tech, finance
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


class WSJScraper(BaseScraper):
    """Scraper especializado para Wall Street Journal."""
    
    BASE_URL = "https://www.wsj.com"
    MIN_SUCCESS_RATE = 0.2  # 20% - paywall
    HAS_PAYWALL = True
    
    CATEGORIES = {
        "markets": "https://www.wsj.com/news/markets",
        "economy": "https://www.wsj.com/news/economy",
        "business": "https://www.wsj.com/news/business",
        "tech": "https://www.wsj.com/news/technology",
        "finance": "https://www.wsj.com/news/finance",
        "world": "https://www.wsj.com/news/world",
    }
    
    SELECTORS = {
        "article_links": [
            "a.WSJTheme--headline--unZqjb45",
            "a[data-type='article']",
            "h3.WSJTheme--headline--unZqjb45 a",
        ],
        "title": [
            "h1.wsj-article-headline",
            "h1[data-testid='headline']",
            "h1.ArticleHeader_headline",
        ],
        "text": [
            "div.article-content p",
            "div.ArticleBody p",
            "section[data-testid='article-content'] p",
        ],
        "date": [
            "time[data-testid='timestamp']",
            "time.timestamp",
        ],
        "author": [
            "span[itemprop='name']",
            "a.author-link",
        ],
    }
    
    def __init__(self, scraper):
        """Inicializa o scraper."""
        super().__init__(scraper, source_id="wsj")
    
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
            category: Categoria (markets, economy, business, etc.)
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
        logger.info(f"Fetching WSJ articles from {category}: {url}")
        
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
                        if href and "/articles/" in href:
                            urls.add(href)
                            if len(urls) >= limit:
                                break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
                
                if len(urls) >= limit:
                    break
            
            result = list(urls)[:limit]
            logger.info(f"Found {len(result)} WSJ articles")
            return result
        
        except Exception as e:
            logger.error(f"Error collecting WSJ URLs: {e}")
            return []
