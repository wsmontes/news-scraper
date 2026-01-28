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
from typing import Literal
from news_scraper.browser import ProfessionalScraper


class BloombergScraper:
    """Scraper especializado para Bloomberg Brasil."""
    
    def __init__(self, scraper: ProfessionalScraper):
        """
        Args:
            scraper: Instância do ProfessionalScraper já inicializada
        """
        self.scraper = scraper
        self.base_url = "https://www.bloomberg.com.br"
    
    def get_latest_articles(
        self,
        category: Literal["mercados", "economia", "politica", "empresas"] | None = None,
        limit: int = 20,
    ) -> list[str]:
        """
        Extrai URLs dos artigos mais recentes.
        
        Args:
            category: Categoria específica (None = homepage)
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
        
        print(f"✓ {len(sorted_urls)} URLs encontradas")
        
        return sorted_urls
    
    def get_mercados_articles(self, limit: int = 20) -> list[str]:
        """Atalho para artigos de Mercados."""
        return self.get_latest_articles(category="mercados", limit=limit)
    
    def get_economia_articles(self, limit: int = 20) -> list[str]:
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
