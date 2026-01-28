"""
Scraper especializado para Money Times (moneytimes.com.br).

Money Times é um portal de notícias financeiras brasileiro focado em
investimentos, mercados e economia.
Estrutura do site testada e validada em janeiro/2026.

Características:
- Site acessível (não requer anti-detecção especial)
- URLs seguem padrão: /titulo-slug-codigo/
- Código no final da URL (ex: -igdl/, -lmrs/)
- Encontradas ~78 URLs na homepage
"""

from __future__ import annotations
from typing import List, Optional
from datetime import datetime
import logging

from ..base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class MoneyTimesScraper(BaseScraper):
    """Scraper especializado para Money Times."""
    
    BASE_URL = "https://www.moneytimes.com.br"
    MIN_SUCCESS_RATE = 0.6  # 60%
    HAS_PAYWALL = False
    
    def __init__(self, scraper):
        """Inicializa o scraper."""
        super().__init__(scraper, source_id="moneytimes")
    
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
            category: Não usado (Money Times usa apenas homepage)
            limit: Número máximo de URLs para retornar
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        logger.info(f"Coletando de: {self.BASE_URL}")
        
        # Carregar página
        self.scraper.get_page(self.BASE_URL, wait_time=3)
        
        # Scroll para carregar mais conteúdo
        self.scraper.scroll_and_load(scroll_pause=1.0, max_scrolls=2)
        
        # Extrair todos os links
        all_links = self.scraper.driver.find_elements('css selector', 'a')
        
        article_urls: set[str] = set()
        
        for link in all_links:
            href = link.get_attribute('href')
            
            if not href or 'moneytimes.com.br' not in href:
                continue
            
            # URLs de artigos são longas (> 50 chars) e terminam com código
            # Exemplos: -igdl/, -lmrs/, -jals/, -mabe/
            if len(href) > 50 and '-' in href.split('/')[-2]:
                # Excluir páginas de navegação e páginas especiais
                if not any(x in href.lower() for x in [
                    '/autor/', '/tag/', '/categoria/', '/page/', 
                    '/busca/', '/search/', '/sobre/', '/contato/',
                    '/central-de-', '/cotacoes/', '/monitor-',
                    'utm_', 'facebook', 'twitter', 'linkedin',
                    'newsletter', 'cadastro'
                ]):
                    article_urls.add(href)
            
            if len(article_urls) >= limit * 2:  # Coletar extras para filtrar depois
                break
        
        # Ordenar e limitar
        sorted_urls = sorted(article_urls)[:limit]
        
        logger.info(f"✓ {len(sorted_urls)} URLs encontradas")
        
        return sorted_urls


def scrape_moneytimes(
    limit: int = 20,
    headless: bool = True,
) -> list[str]:
    """
    Função de conveniência para scraping do Money Times.
    
    Args:
        limit: Número de artigos
        headless: Executar em modo headless
        
    Returns:
        Lista de URLs de artigos
        
    Example:
        >>> from news_scraper.moneytimes_scraper import scrape_moneytimes
        >>> urls = scrape_moneytimes(limit=10)
        >>> print(f"Coletadas {len(urls)} URLs")
    """
    from news_scraper.browser import BrowserConfig, ProfessionalScraper
    
    config = BrowserConfig(headless=headless)
    
    with ProfessionalScraper(config) as scraper:
        moneytimes = MoneyTimesScraper(scraper)
        return moneytimes.get_latest_articles(limit=limit)
