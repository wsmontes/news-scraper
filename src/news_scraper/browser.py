from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


@dataclass
class BrowserConfig:
    headless: bool = True
    timeout: int = 30
    window_size: tuple[int, int] = (1920, 1080)
    user_agent: str | None = None
    implicit_wait: float = 10.0


class ProfessionalScraper:
    """Scraper profissional com Selenium para sites JavaScript-heavy."""

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or BrowserConfig()
        self.driver = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self) -> None:
        """Inicia o browser."""
        options = ChromeOptions()

        if self.config.headless:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")

        if self.config.user_agent:
            options.add_argument(f"user-agent={self.config.user_agent}")
        else:
            # User agent realista
            options.add_argument(
                "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

        # Anti-detecção
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(self.config.implicit_wait)

        # Remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def stop(self) -> None:
        """Fecha o browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get_page(self, url: str, wait_selector: str | None = None, wait_time: int | None = None) -> str:
        """Carrega página e retorna HTML renderizado.

        Args:
            url: URL para carregar
            wait_selector: CSS selector para aguardar antes de retornar (ex.: 'article', '.content')
            wait_time: Tempo adicional de espera em segundos
        """
        if not self.driver:
            raise RuntimeError("Browser não iniciado. Use .start() ou context manager.")

        self.driver.get(url)

        # Aguarda elemento específico se fornecido
        if wait_selector:
            wait = WebDriverWait(self.driver, self.config.timeout)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))

        # Aguarda tempo adicional se fornecido
        if wait_time:
            time.sleep(wait_time)

        # Scroll para carregar lazy-load
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        return self.driver.page_source

    def extract_links(
        self,
        url: str,
        selector: str,
        filter_contains: str | None = None,
        wait_time: int = 3,
    ) -> list[str]:
        """Extrai links de uma página.

        Args:
            url: URL da página
            selector: CSS selector para links (ex.: 'a[href*="/noticias/"]')
            filter_contains: Filtrar apenas URLs que contêm este texto
            wait_time: Tempo de espera após carregar
        """
        html = self.get_page(url, wait_time=wait_time)

        from bs4 import BeautifulSoup
        from urllib.parse import urljoin

        soup = BeautifulSoup(html, "lxml")
        links = soup.select(selector)

        urls: set[str] = set()
        for link in links:
            href = link.get("href")
            if not href:
                continue

            full_url = urljoin(url, href)

            if filter_contains and filter_contains not in full_url:
                continue

            urls.add(full_url)

        return sorted(urls)

    def scroll_and_load(self, scroll_pause: float = 2.0, max_scrolls: int = 5) -> str:
        """Scroll progressivo para carregar conteúdo lazy-load.

        Útil para feeds infinitos.
        """
        if not self.driver:
            raise RuntimeError("Browser não iniciado.")

        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for _ in range(max_scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        return self.driver.page_source


def scrape_with_browser(
    url: str,
    headless: bool = True,
    wait_selector: str | None = None,
    wait_time: int | None = None,
) -> str:
    """Helper rápido para scraping com browser."""

    config = BrowserConfig(headless=headless)

    with ProfessionalScraper(config) as scraper:
        return scraper.get_page(url, wait_selector, wait_time)
