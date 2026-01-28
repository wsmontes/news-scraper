"""
Testes para o scraper da Reuters.

Garante que os metadados completos são extraídos corretamente.
"""

import pytest
from datetime import datetime
from news_scraper.sources.en import ReutersScraper
from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.extract import extract_article_metadata


@pytest.fixture(scope="module")
def scraper():
    """Fixture com scraper configurado."""
    config = BrowserConfig(headless=True)
    scraper = ProfessionalScraper(config)
    scraper.start()
    yield scraper
    scraper.stop()


@pytest.fixture(scope="module")
def reuters_scraper(scraper):
    """Fixture com ReutersScraper."""
    return ReutersScraper(scraper)


def test_reuters_get_latest_articles(reuters_scraper):
    """Testa coleta de URLs mais recentes."""
    urls = reuters_scraper.get_latest_articles(limit=10)
    
    assert len(urls) > 0, "Não coletou nenhuma URL"
    assert len(urls) <= 10, f"Coletou mais URLs ({len(urls)}) do que o limite (10)"
    
    # Verificar se são URLs válidas
    for url in urls:
        assert url.startswith("https://"), f"URL inválida: {url}"
        assert "reuters.com" in url, f"URL não é da Reuters: {url}"


def test_reuters_markets_category(reuters_scraper):
    """Testa categoria markets."""
    urls = reuters_scraper.get_latest_articles(category="markets", limit=5)
    
    assert len(urls) > 0, "Não coletou URLs da categoria markets"


def test_reuters_extract_metadata(reuters_scraper, scraper):
    """Testa extração de metadados de um artigo."""
    urls = reuters_scraper.get_latest_articles(limit=3)
    
    if not urls:
        pytest.skip("Nenhuma URL coletada")
    
    url = urls[0]
    metadata = extract_article_metadata(url, scraper.driver)
    
    assert metadata is not None, "Metadados não extraídos"
    assert "title" in metadata, "Título não extraído"
    assert "text" in metadata, "Texto não extraído"
    assert len(metadata.get("text", "")) > 50, "Texto muito curto"


def test_reuters_multiple_articles_metadata(reuters_scraper, scraper):
    """Testa extração de metadados de múltiplos artigos."""
    urls = reuters_scraper.get_latest_articles(limit=5)
    
    if not urls:
        pytest.skip("Nenhuma URL coletada")
    
    success_count = 0
    for url in urls[:3]:
        try:
            metadata = extract_article_metadata(url, scraper.driver)
            if metadata and metadata.get("text") and len(metadata["text"]) > 50:
                success_count += 1
        except Exception as e:
            print(f"Erro ao extrair {url}: {e}")
    
    success_rate = success_count / min(3, len(urls))
    assert success_rate >= 0.5, f"Taxa de sucesso muito baixa: {success_rate:.1%}"
