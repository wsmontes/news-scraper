"""
Teste integrado para todos os scrapers de fontes financeiras.

Valida que todos os scrapers:
1. Coletam URLs corretamente
2. Extraem metadados completos
3. Mantêm qualidade mínima (80% de sucesso)
4. Extraem datas válidas
"""

import pytest
from datetime import datetime
from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.sources.pt import InfoMoneyScraper, ValorScraper, EInvestidorScraper, MoneyTimesScraper
from news_scraper.sources.en import BloombergScraper
from news_scraper.extract import extract_article_metadata


# Configuração de todos os scrapers
SCRAPERS = [
    ("InfoMoney", InfoMoneyScraper, "infomoney.com.br"),
    ("Valor Econômico", ValorScraper, "valor.globo.com"),
    ("Bloomberg Brasil", BloombergScraper, "bloomberg.com.br"),
    ("E-Investidor", EInvestidorScraper, "einvestidor.estadao.com.br"),
    ("Money Times", MoneyTimesScraper, "moneytimes.com.br"),
]


@pytest.fixture(scope="module")
def scraper():
    """Fixture com scraper configurado."""
    config = BrowserConfig(headless=True)
    scraper = ProfessionalScraper(config)
    scraper.start()
    yield scraper
    scraper.stop()


@pytest.mark.parametrize("source_name,scraper_class,domain", SCRAPERS)
def test_all_sources_collect_urls(scraper, source_name, scraper_class, domain):
    """Testa que cada fonte consegue coletar URLs."""
    source_scraper = scraper_class(scraper)
    urls = source_scraper.get_latest_articles(limit=3)
    
    assert len(urls) > 0, f"{source_name}: Deve retornar pelo menos 1 URL"
    assert len(urls) <= 3, f"{source_name}: Não deve exceder o limite"
    
    for url in urls:
        assert domain in url, f"{source_name}: URL deve conter domínio {domain}"
        assert url.startswith("http"), f"{source_name}: URL deve ser válida"
    
    print(f"\n✓ {source_name}: {len(urls)} URLs coletadas")


@pytest.mark.parametrize("source_name,scraper_class,domain", SCRAPERS)
def test_all_sources_extract_metadata(scraper, source_name, scraper_class, domain):
    """Testa que cada fonte extrai metadados corretamente."""
    source_scraper = scraper_class(scraper)
    urls = source_scraper.get_latest_articles(limit=1)
    
    assert len(urls) > 0, f"{source_name}: Deve ter URLs para testar"
    
    url = urls[0]
    scraper.get_page(url, wait_time=3)
    article = extract_article_metadata(url, scraper.driver)
    
    # Validações essenciais
    errors = []
    
    if not article.title:
        errors.append("Título não extraído")
    elif len(article.title) < 10:
        errors.append("Título muito curto")
    
    if not article.date_published:
        errors.append("Data não extraída")
    elif not isinstance(article.date_published, datetime):
        errors.append("Data não é datetime")
    elif article.date_published.year < 2020:
        errors.append("Data inválida")
    
    if not article.text:
        errors.append("Texto não extraído")
    elif len(article.text) < 100:
        errors.append("Texto muito curto")
    
    if not article.source:
        errors.append("Source não identificada")
    
    if not article.scraped_at:
        errors.append("scraped_at não preenchido")
    
    if errors:
        pytest.fail(f"{source_name}: {', '.join(errors)}")
    
    print(f"\n✓ {source_name}: Metadados extraídos com sucesso")
    print(f"  Título: {article.title[:50]}...")
    print(f"  Data: {article.date_published}")
    print(f"  Autor: {article.author or 'N/A'}")
    print(f"  Texto: {len(article.text)} chars")


def test_all_sources_quality_threshold(scraper):
    """Testa que todas as fontes mantêm qualidade mínima de 80%."""
    results = []
    
    for source_name, scraper_class, domain in SCRAPERS:
        source_scraper = scraper_class(scraper)
        urls = source_scraper.get_latest_articles(limit=3)
        
        if not urls:
            continue
        
        success_count = 0
        
        for url in urls:
            try:
                scraper.get_page(url, wait_time=2)
                article = extract_article_metadata(url, scraper.driver)
                
                # Verificar se campos essenciais existem
                has_title = article.title and len(article.title) > 10
                has_date = article.date_published and isinstance(article.date_published, datetime)
                has_text = article.text and len(article.text) > 100
                
                if has_title and has_date and has_text:
                    success_count += 1
            except Exception as e:
                print(f"Erro em {url}: {e}")
                continue
        
        success_rate = success_count / len(urls) if urls else 0
        results.append((source_name, success_rate, success_count, len(urls)))
    
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO DE QUALIDADE")
    print("=" * 70)
    
    for source_name, rate, success, total in results:
        status = "✅" if rate >= 0.8 else "⚠️"
        print(f"{status} {source_name:20} {rate:>6.1%} ({success}/{total})")
    
    # Falhar se alguma fonte estiver abaixo do threshold
    failures = [name for name, rate, _, _ in results if rate < 0.8]
    
    if failures:
        pytest.fail(
            f"Fontes abaixo do threshold de 80%: {', '.join(failures)}"
        )


def test_all_sources_date_extraction(scraper):
    """Testa especificamente a extração de datas de todas as fontes."""
    date_results = []
    
    for source_name, scraper_class, domain in SCRAPERS:
        source_scraper = scraper_class(scraper)
        urls = source_scraper.get_latest_articles(limit=2)
        
        if not urls:
            continue
        
        dates_extracted = 0
        valid_dates = 0
        
        for url in urls:
            try:
                scraper.get_page(url, wait_time=2)
                article = extract_article_metadata(url, scraper.driver)
                
                if article.date_published:
                    dates_extracted += 1
                    
                    if (isinstance(article.date_published, datetime) and
                        2020 <= article.date_published.year <= 2030):
                        valid_dates += 1
            except Exception as e:
                print(f"Erro em {url}: {e}")
                continue
        
        date_results.append((source_name, valid_dates, dates_extracted, len(urls)))
    
    print("\n" + "=" * 70)
    print("📅 RELATÓRIO DE EXTRAÇÃO DE DATAS")
    print("=" * 70)
    
    for source_name, valid, extracted, total in date_results:
        rate = valid / total if total > 0 else 0
        status = "✅" if rate >= 0.8 else "⚠️"
        print(f"{status} {source_name:20} {rate:>6.1%} ({valid}/{total} válidas)")
    
    # Falhar se alguma fonte não extrair datas adequadamente
    failures = [
        name for name, valid, extracted, total in date_results
        if (valid / total if total > 0 else 0) < 0.8
    ]
    
    if failures:
        pytest.fail(
            f"Fontes com problemas na extração de datas: {', '.join(failures)}"
        )


def test_compare_all_sources():
    """Teste comparativo de todas as fontes (apenas informativo)."""
    print("\n" + "=" * 70)
    print("📋 COMPARATIVO DE SCRAPERS")
    print("=" * 70)
    print(f"{'Fonte':<25} {'Domínio':<30} {'Status'}")
    print("-" * 70)
    
    for source_name, scraper_class, domain in SCRAPERS:
        print(f"{source_name:<25} {domain:<30} ✓")
    
    print("=" * 70)
    print(f"Total: {len(SCRAPERS)} fontes suportadas")
