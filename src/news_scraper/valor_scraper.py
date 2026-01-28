"""
Scraper especializado para Valor Econômico (valor.globo.com).

Valor Econômico é o principal jornal de economia e finanças do Brasil,
parte do Grupo Globo. Estrutura do site testada em janeiro/2026.

Características:
- Site JavaScript-heavy (requer Selenium)
- URLs seguem padrão: /categoria/noticia/ano/mes/dia/titulo-slug/
- Data inclusa na URL facilita extração
- Categorias: /financas/, /empresas/, /mercados/, /mundo/, etc.
"""

from __future__ import annotations
from typing import Literal
from news_scraper.browser import ProfessionalScraper


class ValorScraper:
    """Scraper especializado para Valor Econômico."""
    
    def __init__(self, scraper: ProfessionalScraper):
        """
        Args:
            scraper: Instância do ProfessionalScraper já inicializada
        """
        self.scraper = scraper
        self.base_url = "https://valor.globo.com"
    
    def get_latest_articles(
        self,
        category: Literal["financas", "empresas", "mercados", "mundo", "politica", "brasil"] | None = None,
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
        self.scraper.scroll_and_load(scroll_pause=2.0, max_scrolls=3)
        
        # Extrair todos os links
        all_links = self.scraper.driver.find_elements('css selector', 'a')
        
        article_urls: set[str] = set()
        
        for link in all_links:
            href = link.get_attribute('href')
            
            if not href or 'valor.globo.com' not in href:
                continue
            
            # URLs de artigos têm data no formato: /ano/mes/dia/
            # Ex: /financas/noticia/2026/01/28/titulo-da-noticia.ghtml
            if '/noticia/' in href and '/20' in href:  # Ano 20xx
                # Verificar se tem estrutura de data
                parts = href.split('/')
                if len(parts) >= 7:  # Mínimo para ter /noticia/ano/mes/dia/titulo
                    # Excluir páginas de navegação
                    if not any(x in href.lower() for x in [
                        '/autor/', '/tag/', '/busca/', '/search/',
                        'utm_', 'facebook', 'twitter', 'linkedin',
                        'newsletter', 'assine'
                    ]):
                        article_urls.add(href)
            
            if len(article_urls) >= limit * 2:
                break
        
        # Ordenar e limitar
        sorted_urls = sorted(article_urls)[:limit]
        
        print(f"✓ {len(sorted_urls)} URLs encontradas")
        
        return sorted_urls
    
    def get_financas_articles(self, limit: int = 20) -> list[str]:
        """Atalho para artigos de Finanças."""
        return self.get_latest_articles(category="financas", limit=limit)
    
    def get_mercados_articles(self, limit: int = 20) -> list[str]:
        """Atalho para artigos de Mercados."""
        return self.get_latest_articles(category="mercados", limit=limit)
    
    def get_empresas_articles(self, limit: int = 20) -> list[str]:
        """Atalho para artigos de Empresas."""
        return self.get_latest_articles(category="empresas", limit=limit)


def scrape_valor(
    category: str | None = None,
    limit: int = 20,
    headless: bool = True,
) -> list[str]:
    """
    Função de conveniência para scraping do Valor Econômico.
    
    Args:
        category: Categoria ('financas', 'mercados', etc.) ou None para homepage
        limit: Número de artigos
        headless: Executar em modo headless
        
    Returns:
        Lista de URLs de artigos
        
    Example:
        >>> from news_scraper.valor_scraper import scrape_valor
        >>> urls = scrape_valor(category='financas', limit=10)
        >>> print(f"Coletadas {len(urls)} URLs")
    """
    from news_scraper.browser import BrowserConfig, ProfessionalScraper
    
    config = BrowserConfig(headless=headless)
    
    with ProfessionalScraper(config) as scraper:
        valor = ValorScraper(scraper)
        
        if category:
            return valor.get_latest_articles(category=category, limit=limit)  # type: ignore
        else:
            return valor.get_latest_articles(limit=limit)
