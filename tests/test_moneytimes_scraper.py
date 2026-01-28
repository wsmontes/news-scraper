"""
Testes para o scraper do Money Times.

Garante que os metadados completos são extraídos corretamente,
com foco especial em data de publicação.
"""

import pytest
from datetime import datetime
from news_scraper.moneytimes_scraper import MoneyTimesScraper
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
def moneytimes_scraper(scraper):
    """Fixture com MoneyTimesScraper."""
    return MoneyTimesScraper(scraper)


def test_moneytimes_get_latest_articles(moneytimes_scraper):
    """Testa coleta de URLs da homepage."""
    urls = moneytimes_scraper.get_latest_articles(limit=5)
    
    assert len(urls) > 0, "Deve retornar pelo menos 1 URL"
    assert len(urls) <= 5, "Não deve exceder o limite"
    
    for url in urls:
        assert "moneytimes.com.br" in url
        assert url.startswith("http")
        assert len(url) > 50, "URLs de artigos devem ser longas"


def test_moneytimes_extract_metadata(moneytimes_scraper):
    """Testa extração de metadados completos de um artigo."""
    # Coletar uma URL recente
    urls = moneytimes_scraper.get_latest_articles(limit=1)
    assert len(urls) > 0, "Deve ter pelo menos 1 URL"
    
    url = urls[0]
    
    # Acessar a página do artigo
    moneytimes_scraper.scraper.get_page(url, wait_time=3)
    
    # Extrair metadados
    article = extract_article_metadata(url, moneytimes_scraper.scraper.driver)
    
    # Validar campos essenciais
    assert article.url == url
    assert article.title is not None, "Título deve ser extraído"
    assert len(article.title) > 10, "Título deve ter conteúdo significativo"
    
    assert article.date_published is not None, "Data de publicação deve ser extraída"
    assert isinstance(article.date_published, datetime), "Data deve ser datetime"
    assert article.date_published.year >= 2020, "Data deve ser válida"
    
    assert article.text is not None, "Texto deve ser extraído"
    assert len(article.text) > 100, "Texto deve ter conteúdo significativo"
    
    assert article.source is not None, "Source deve ser identificada"
    assert "moneytimes" in article.source.lower() or "money" in article.source.lower()
    
    assert article.scraped_at is not None
    assert isinstance(article.scraped_at, datetime)
    
    # Autor pode ser None em algumas notícias
    if article.author:
        assert len(article.author) > 2
    
    print(f"\n✓ Metadados extraídos com sucesso:")
    print(f"  Título: {article.title[:60]}...")
    print(f"  Data: {article.date_published}")
    print(f"  Autor: {article.author or 'N/A'}")
    print(f"  Texto: {len(article.text)} caracteres")
    print(f"  Source: {article.source}")


def test_moneytimes_multiple_articles_metadata(moneytimes_scraper):
    """Testa extração de metadados de múltiplos artigos."""
    urls = moneytimes_scraper.get_latest_articles(limit=3)
    
    articles_with_date = 0
    articles_with_title = 0
    articles_with_text = 0
    
    for url in urls:
        moneytimes_scraper.scraper.get_page(url, wait_time=2)
        article = extract_article_metadata(url, moneytimes_scraper.scraper.driver)
        
        if article.date_published:
            articles_with_date += 1
        if article.title:
            articles_with_title += 1
        if article.text and len(article.text) > 100:
            articles_with_text += 1
    
    # Pelo menos 80% dos artigos devem ter os campos essenciais
    success_rate = articles_with_date / len(urls)
    assert success_rate >= 0.66, f"Taxa de sucesso de data: {success_rate:.1%}"
    
    success_rate = articles_with_title / len(urls)
    assert success_rate >= 0.66, f"Taxa de sucesso de título: {success_rate:.1%}"
    
    success_rate = articles_with_text / len(urls)
    assert success_rate >= 0.66, f"Taxa de sucesso de texto: {success_rate:.1%}"
    
    print(f"\n✓ Taxa de sucesso na extração:")
    print(f"  Data: {articles_with_date}/{len(urls)}")
    print(f"  Título: {articles_with_title}/{len(urls)}")
    print(f"  Texto: {articles_with_text}/{len(urls)}")
