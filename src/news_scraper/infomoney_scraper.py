"""
Scraper especializado para InfoMoney (www.infomoney.com.br).

O InfoMoney é um portal de notícias financeiras brasileiro.
Estrutura do site testada e validada em janeiro/2026.

Características:
- Site JavaScript-heavy (requer Selenium)
- URLs de artigos seguem padrão: /categoria/titulo-slug/
- Artigos longos geralmente têm URLs > 60 caracteres
- Categorias principais: /mercados/, /economia/, /investimentos/, etc.
"""

from __future__ import annotations
from typing import Literal
from news_scraper.browser import ProfessionalScraper


class InfoMoneyScraper:
    """Scraper especializado para InfoMoney."""
    
    def __init__(self, scraper: ProfessionalScraper):
        """
        Args:
            scraper: Instância do ProfessionalScraper já inicializada
        """
        self.scraper = scraper
        self.base_url = "https://www.infomoney.com.br"
    
    def get_latest_articles(
        self,
        category: Literal["mercados", "economia", "investimentos", "negocios", "carreira"] | None = None,
        limit: int = 20,
    ) -> list[str]:
        """
        Extrai URLs dos artigos mais recentes.
        
        Args:
            category: Categoria específica (None = homepage com todas)
            limit: Número máximo de URLs para retornar
            
        Returns:
            Lista de URLs de artigos
        """
        if category:
            url = f"{self.base_url}/{category}/"
        else:
            url = self.base_url
        
        print(f"Coletando de: {url}")
        
        # Carregar página
        self.scraper.get_page(url, wait_time=3)
        
        # Scroll para carregar mais conteúdo
        self.scraper.scroll_and_load(scroll_pause=1.5, max_scrolls=3)
        
        # Extrair todos os links
        all_links = self.scraper.driver.find_elements('css selector', 'a')
        
        article_urls: set[str] = set()
        
        for link in all_links:
            href = link.get_attribute('href')
            
            if not href or 'infomoney.com.br' not in href:
                continue
            
            # Filtrar por categoria se especificada
            if category and f'/{category}/' not in href:
                continue
            
            # URLs de artigos são longas (> 60 chars) e têm estrutura /categoria/titulo-slug/
            if len(href) > 60 and href.count('/') >= 4:
                # Excluir páginas de navegação
                if not any(x in href.lower() for x in [
                    '/autor/', '/tag/', '/page/', '/busca/', '/search/',
                    'utm_', 'facebook', 'twitter', 'linkedin'
                ]):
                    article_urls.add(href)
            
            if len(article_urls) >= limit * 2:  # Coletar extras para filtrar depois
                break
        
        # Ordenar e limitar
        sorted_urls = sorted(article_urls)[:limit]
        
        print(f"✓ {len(sorted_urls)} URLs encontradas")
        
        return sorted_urls
    
    def get_mercados_articles(self, limit: int = 20) -> list[str]:
        """Atalho para artigos de Mercados."""
        return self.get_latest_articles(category="mercados", limit=limit)
    
    def get_economia_articles(self, limit: int = 20) -> list[str]:
        """Atalho para artigos de Economia."""
        return self.get_latest_articles(category="economia", limit=limit)
    
    def get_investimentos_articles(self, limit: int = 20) -> list[str]:
        """Atalho para artigos de Investimentos."""
        return self.get_latest_articles(category="investimentos", limit=limit)


def scrape_infomoney(
    category: str | None = None,
    limit: int = 20,
    headless: bool = True,
) -> list[str]:
    """
    Função de conveniência para scraping do InfoMoney.
    
    Args:
        category: Categoria ('mercados', 'economia', etc.) ou None para homepage
        limit: Número de artigos
        headless: Executar em modo headless
        
    Returns:
        Lista de URLs de artigos
        
    Example:
        >>> from news_scraper.infomoney_scraper import scrape_infomoney
        >>> urls = scrape_infomoney(category='mercados', limit=10)
        >>> print(f"Coletadas {len(urls)} URLs")
    """
    from news_scraper.browser import BrowserConfig, ProfessionalScraper
    
    config = BrowserConfig(headless=headless)
    
    with ProfessionalScraper(config) as scraper:
        infomoney = InfoMoneyScraper(scraper)
        
        if category:
            return infomoney.get_latest_articles(category=category, limit=limit)  # type: ignore
        else:
            return infomoney.get_latest_articles(limit=limit)
