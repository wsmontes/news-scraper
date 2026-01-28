"""
Scraper especializado para Bloomberg Brasil (bloomberg.com.br).

Bloomberg Brasil é a versão brasileira do portal internacional de notícias
financeiras Bloomberg. Estrutura do site testada em janeiro/2026.

Características:
- Site JavaScript-heavy (requer Selenium)
- URLs seguem padrão internacional Bloomberg
- Foco em notícias de mercado em tempo real
- Conteúdo em português brasileiro
"""

from __future__ import annotations
from typing import Literal, List, Optional
from datetime import datetime
import logging

from ..base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BloombergScraper(BaseScraper):
    """Scraper especializado para Bloomberg Brasil."""
    
    BASE_URL = "https://www.bloomberg.com.br"
    MIN_SUCCESS_RATE = 0.5  # 50%
    HAS_PAYWALL = False
    
    def __init__(self, scraper):
        """Inicializa o scraper."""
        super().__init__(scraper, source_id="bloomberg")
    
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
            category: Categoria específica (mercados, economia, politica, empresas)
            limit: Número máximo de URLs para retornar
            start_date: Data inicial (não implementado ainda)
            end_date: Data final (não implementado ainda)
            
        Returns:
            Lista de URLs coletadas
        """
        if category:
            url = f"{self.BASE_URL}/{category}/"
        else:
            url = self.BASE_URL
        
        logger.info(f"Coletando de: {url}")
        
        # Carregar página
        self.scraper.get_page(url, wait_time=4)
        
        # Scroll para carregar mais conteúdo
        self.scraper.scroll_and_load(scroll_pause=2.0, max_scrolls=4)
        
        # Extrair todos os links
        all_links = self.scraper.driver.find_elements('css selector', 'a')
        
        article_urls: set[str] = set()
        
        for link in all_links:
            href = link.get_attribute('href')
            
            if not href or 'bloomberg.com.br' not in href:
                continue
            
            # URLs de artigos Bloomberg geralmente têm estrutura específica
            # Ex: /news/articles/YYYY-MM-DD/titulo-da-noticia
            if '/news/' in href or '/artigo/' in href or '/noticias/' in href:
                # URLs de artigos são razoavelmente longas
                if len(href) > 50:
                    # Excluir páginas de navegação e especiais
                    if not any(x in href.lower() for x in [
                        '/autor/', '/colunista/', '/tag/', '/busca/', '/search/',
                        '/about/', '/sobre/', '/contato/', '/newsletter/',
                        'utm_', 'facebook', 'twitter', 'linkedin',
                        'assine', 'cadastro', 'register', 'subscribe'
                    ]):
                        article_urls.add(href)
            
            if len(article_urls) >= limit * 2:
                break
        
        # Ordenar e limitar
        sorted_urls = sorted(article_urls)[:limit]
        
        logger.info(f"✓ {len(sorted_urls)} URLs encontradas")
        
        return sorted_urls
    
    def get_mercados_articles(self, limit: int = 20) -> List[str]:
        """Atalho para artigos de Mercados."""
        return self.get_latest_articles(category="mercados", limit=limit)
    
    def get_economia_articles(self, limit: int = 20) -> List[str]:
        """Atalho para artigos de Economia."""
        return self.get_latest_articles(category="economia", limit=limit)


def scrape_bloomberg(
    category: str | None = None,
    limit: int = 20,
    headless: bool = True,
) -> list[str]:
    """
    Função de conveniência para scraping do Bloomberg Brasil.
    
    Args:
        category: Categoria ('mercados', 'economia', etc.) ou None para homepage
        limit: Número de artigos
        headless: Executar em modo headless
        
    Returns:
        Lista de URLs de artigos
        
    Example:
        >>> from news_scraper.bloomberg_scraper import scrape_bloomberg
        >>> urls = scrape_bloomberg(category='mercados', limit=10)
        >>> print(f"Coletadas {len(urls)} URLs")
    """
    from news_scraper.browser import BrowserConfig, ProfessionalScraper
    
    config = BrowserConfig(headless=headless)
    
    with ProfessionalScraper(config) as scraper:
        bloomberg = BloombergScraper(scraper)
        
        if category:
            return bloomberg.get_latest_articles(category=category, limit=limit)  # type: ignore
        else:
            return bloomberg.get_latest_articles(limit=limit)
