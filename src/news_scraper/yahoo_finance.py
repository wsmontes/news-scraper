from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .browser import ProfessionalScraper


class YahooFinanceScraper:
    """Scraper especializado para Yahoo Finance Brasil."""

    BASE_URL = "https://br.finance.yahoo.com"

    def __init__(self, scraper: ProfessionalScraper):
        self.scraper = scraper

    def get_latest_news_urls(self, limit: int = 20) -> list[str]:
        """Extrai URLs das últimas notícias."""

        # Página de notícias
        news_page = f"{self.BASE_URL}/noticias/"

        # Carrega e espera renderizar
        html = self.scraper.get_page(news_page, wait_time=5)

        # Scroll para carregar mais
        html = self.scraper.scroll_and_load(scroll_pause=3.0, max_scrolls=5)

        soup = BeautifulSoup(html, "lxml")

        # Yahoo Finance: encontra todos os links
        urls: set[str] = set()

        for link in soup.find_all("a", href=True):
            href = link["href"]

            # Múltiplos padrões de URL do Yahoo Finance
            if any(
                pattern in href
                for pattern in [
                    "/noticias/",
                    "/news/",
                    "finance.yahoo.com/noticias",
                    "finance.yahoo.com/news",
                ]
            ):
                # Evita URLs de navegação
                if any(skip in href for skip in ["?", "#", "/video", "/galeria", "/search"]):
                    continue

                full_url = urljoin(self.BASE_URL, href)
                
                # Garante que é URL completa e válida
                if full_url.startswith("http") and "finance.yahoo.com" in full_url:
                    # Remove query params e fragments
                    full_url = full_url.split("?")[0].split("#")[0]
                    urls.add(full_url)

                if len(urls) >= limit:
                    break

        return sorted(urls)[:limit]

    def get_archive_urls(self, category: str = "", limit: int = 50) -> list[str]:
        """Extrai URLs de arquivo/categoria específica.

        Args:
            category: Categoria (ex.: 'mercados', 'acoes', 'economia')
            limit: Máximo de URLs
        """

        if category:
            url = f"{self.BASE_URL}/{category}/"
        else:
            url = f"{self.BASE_URL}/noticias/"

        html = self.scraper.scroll_and_load(scroll_pause=2.0, max_scrolls=5)
        soup = BeautifulSoup(html, "lxml")

        urls: set[str] = set()
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/noticias/" in href or f"/{category}/" in href:
                full_url = urljoin(self.BASE_URL, href)
                if "finance.yahoo.com" in full_url:
                    urls.add(full_url)

                if len(urls) >= limit:
                    break

        return sorted(urls)[:limit]
