"""
Financial Times (FT) Scraper - Premium financial news.

Site: https://www.ft.com
Características:
- Paywall forte
- Conteúdo premium
- Categorias: markets, companies, technology, opinion
- Requer estratégias avançadas de extração
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


class FinancialTimesScraper(BaseScraper):
    """Scraper especializado para Financial Times."""
    
    BASE_URL = "https://www.ft.com"
    MIN_SUCCESS_RATE = 0.2  # 20% - paywall forte
    HAS_PAYWALL = True
    
    CATEGORIES = {
        "markets": "https://www.ft.com/markets",
        "companies": "https://www.ft.com/companies",
        "technology": "https://www.ft.com/technology",
        "opinion": "https://www.ft.com/opinion",
        "world": "https://www.ft.com/world",
        "economics": "https://www.ft.com/global-economy",
    }
    
    SELECTORS = {
        "article_links": [
            "a.js-teaser-heading-link",
            "a[data-trackable='link']",
            "a.o-teaser__heading",
        ],
        "title": [
            "h1.article__headline",
            "h1[data-test-id='headline']",
            "h1.topper__headline",
        ],
        "text": [
            "div.article__content-body p",
            "div[data-test-id='article-text'] p",
            "div.article-body p",
        ],
        "date": [
            "time.article__timestamp",
            "time[datetime]",
        ],
        "author": [
            "a.article__author-link",
            "span.article__author",
        ],
    }
    
    def __init__(self, scraper):
        """Inicializa o scraper."""
        super().__init__(scraper, source_id="ft")
    
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
            category: Categoria (markets, companies, technology, etc.)
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
        logger.info(f"Fetching FT articles from {category}: {url}")
        
        driver = self.scraper.driver
        
        try:
            driver.get(url)
            
            # Esperar carregar
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Scroll para carregar mais conteúdo
            self.scraper._scroll_page(driver, scroll_times=2)
            
            # Coletar links
            urls = set()
            for selector in self.SELECTORS["article_links"]:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        href = elem.get_attribute("href")
                        if href and "/content/" in href:
                            urls.add(href)
                            if len(urls) >= limit:
                                break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
                
                if len(urls) >= limit:
                    break
            
            result = list(urls)[:limit]
            logger.info(f"Found {len(result)} FT articles")
            return result
        
        except Exception as e:
            logger.error(f"Error collecting FT URLs: {e}")
            return []
    
    def extract_article(self, url: str) -> dict:
        """
        Extrai conteúdo de um artigo.
        
        Note: FT tem paywall forte. Este método pode ter sucesso limitado.
        """
        driver = self.scraper.start()
        
        try:
            driver.get(url)
            
            # Esperar carregar
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            
            # Extrair título
            title = None
            for selector in self.SELECTORS["title"]:
                try:
                    elem = driver.find_element(By.CSS_SELECTOR, selector)
                    title = elem.text
                    break
                except:
                    continue
            
            # Extrair texto
            text_parts = []
            for selector in self.SELECTORS["text"]:
                try:
                    elems = driver.find_elements(By.CSS_SELECTOR, selector)
                    text_parts = [e.text for e in elems if e.text.strip()]
                    if text_parts:
                        break
                except:
                    continue
            
            # Extrair data
            date = None
            for selector in self.SELECTORS["date"]:
                try:
                    elem = driver.find_element(By.CSS_SELECTOR, selector)
                    date = elem.get_attribute("datetime") or elem.text
                    break
                except:
                    continue
            
            # Extrair autor
            authors = []
            for selector in self.SELECTORS["author"]:
                try:
                    elems = driver.find_elements(By.CSS_SELECTOR, selector)
                    authors = [e.text for e in elems if e.text.strip()]
                    if authors:
                        break
                except:
                    continue
            
            return {
                "url": url,
                "title": title,
                "text": "\n\n".join(text_parts) if text_parts else None,
                "date": date,
                "authors": authors,
                "source": "Financial Times",
            }
        
        finally:
            self.scraper.quit()
