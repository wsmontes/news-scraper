"""
Scraper especializado para E-Investidor (einvestidor.estadao.com.br).

E-Investidor é o portal de finanças e investimentos do Estadão,
focado em educação financeira e mercado. Estrutura testada em janeiro/2026.

Características:
- Site do Grupo Estadão (moderna arquitetura web)
- URLs seguem padrão: /categoria/titulo-slug/
- Conteúdo com foco em investidores pessoa física
- Categorias: /investimentos/, /mercados/, /colunas/, etc.
"""

from __future__ import annotations
from typing import Literal, List, Optional
from datetime import datetime
import logging

from ..base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class EInvestidorScraper(BaseScraper):
    """Scraper especializado para E-Investidor."""
    
    BASE_URL = "https://einvestidor.estadao.com.br"
    MIN_SUCCESS_RATE = 0.5  # 50%
    HAS_PAYWALL = False
    
    def __init__(self, scraper):
        """Inicializa o scraper."""
        super().__init__(scraper, source_id="einvestidor")
    
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
            category: Categoria específica (investimentos, mercados, colunas, acoes, fundos-imobiliarios)
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
        self.scraper.get_page(url, wait_time=3)
        
        # Scroll para carregar mais conteúdo
        self.scraper.scroll_and_load(scroll_pause=1.5, max_scrolls=3)
        
        # Extrair todos os links
        all_links = self.scraper.driver.find_elements('css selector', 'a')
        
        article_urls: set[str] = set()
        
        for link in all_links:
            href = link.get_attribute('href')
            
            if not href or 'einvestidor.estadao.com.br' not in href:
                continue
            
            # URLs de artigos são longas (> 60 chars) e têm estrutura /categoria/titulo-slug/
            if len(href) > 60 and href.count('/') >= 4:
                # Filtrar por categoria se especificada
                if category and f'/{category}/' not in href:
                    continue
                
                # Excluir páginas de navegação
                if not any(x in href.lower() for x in [
                    '/autor/', '/tag/', '/page/', '/busca/', '/search/',
                    '/sobre/', '/contato/', '/newsletter/',
                    'utm_', 'facebook', 'twitter', 'linkedin',
                    'assine', 'cadastro'
                ]):
                    article_urls.add(href)
            
            if len(article_urls) >= limit * 2:
                break
        
        # Ordenar e limitar
        sorted_urls = sorted(article_urls)[:limit]
        
        logger.info(f"✓ {len(sorted_urls)} URLs encontradas")
        
        return sorted_urls
    
    def get_investimentos_articles(self, limit: int = 20) -> list[str]:
        """Atalho para artigos de Investimentos."""
        return self.get_latest_articles(category="investimentos", limit=limit)
    
    def get_mercados_articles(self, limit: int = 20) -> list[str]:
        """Atalho para artigos de Mercados."""
        return self.get_latest_articles(category="mercados", limit=limit)
    
    def get_acoes_articles(self, limit: int = 20) -> list[str]:
        """Atalho para artigos de Ações."""
        return self.get_latest_articles(category="acoes", limit=limit)


def scrape_einvestidor(
    category: str | None = None,
    limit: int = 20,
    headless: bool = True,
) -> list[str]:
    """
    Função de conveniência para scraping do E-Investidor.
    
    Args:
        category: Categoria ('investimentos', 'mercados', etc.) ou None para homepage
        limit: Número de artigos
        headless: Executar em modo headless
        
    Returns:
        Lista de URLs de artigos
        
    Example:
        >>> from news_scraper.einvestidor_scraper import scrape_einvestidor
        >>> urls = scrape_einvestidor(category='investimentos', limit=10)
        >>> print(f"Coletadas {len(urls)} URLs")
    """
    from news_scraper.browser import BrowserConfig, ProfessionalScraper
    
    config = BrowserConfig(headless=headless)
    
    with ProfessionalScraper(config) as scraper:
        einvestidor = EInvestidorScraper(scraper)
        
        if category:
            return einvestidor.get_latest_articles(category=category, limit=limit)  # type: ignore
        else:
            return einvestidor.get_latest_articles(limit=limit)
