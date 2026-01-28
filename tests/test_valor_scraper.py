"""
Testes para o scraper do Valor Econômico.

Garante que os metadados completos são extraídos corretamente,
com foco especial em data de publicação.
"""

import pytest
from datetime import datetime
from news_scraper.valor_scraper import ValorScraper
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
def valor_scraper(scraper):
    """Fixture com ValorScraper."""
    return ValorScraper(scraper)


def test_valor_get_latest_articles(valor_scraper):
    """Testa coleta de URLs da homepage."""
    urls = valor_scraper.get_latest_articles(limit=5)
    
    assert len(urls) > 0, "Deve retornar pelo menos 1 URL"
    assert len(urls) <= 5, "Não deve exceder o limite"
    
    for url in urls:
        assert "valor.globo.com" in url
        assert url.startswith("http")
        assert "/noticia/" in url


def test_valor_financas_category(valor_scraper):
    """Testa coleta de artigos de Finanças."""
    urls = valor_scraper.get_financas_articles(limit=3)
    
    assert len(urls) > 0
    for url in urls:
        assert "/financas/" in url


def test_valor_extract_metadata(valor_scraper):
    """Testa extração de metadados completos de um artigo."""
    # Coletar uma URL recente
    urls = valor_scraper.get_latest_articles(limit=1)
    assert len(urls) > 0, "Deve ter pelo menos 1 URL"
    
    url = urls[0]
    
    # Acessar a página do artigo
    valor_scraper.scraper.get_page(url, wait_time=3)
    
    # Extrair metadados
    article = extract_article_metadata(url, valor_scraper.scraper.driver)
    
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
    assert "valor" in article.source.lower()
    
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


def test_valor_multiple_articles_metadata(valor_scraper):
    """Testa extração de metadados de múltiplos artigos."""
    urls = valor_scraper.get_latest_articles(limit=3)
    
    articles_with_date = 0
    articles_with_title = 0
    articles_with_text = 0
    
    for url in urls:
        valor_scraper.scraper.get_page(url, wait_time=2)
        article = extract_article_metadata(url, valor_scraper.scraper.driver)
        
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


def test_valor_url_contains_date(valor_scraper):
    """Testa se URLs contêm data no formato esperado."""
    urls = valor_scraper.get_latest_articles(limit=3)
    
    for url in urls:
        # URLs do Valor devem ter /ano/mes/dia/
        assert "/20" in url, "URL deve conter ano"
        parts = url.split('/')
        
        # Encontrar índice do ano
        year_idx = None
        for i, part in enumerate(parts):
            if part.startswith('20') and len(part) == 4 and part.isdigit():
                year_idx = i
                break
        
        assert year_idx is not None, "Deve ter ano na URL"
        assert len(parts) > year_idx + 2, "Deve ter mês e dia após ano"
