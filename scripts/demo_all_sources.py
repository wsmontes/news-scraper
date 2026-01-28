"""
Demonstração de scraping para todas as fontes de notícias financeiras.

Este script demonstra o uso dos scrapers especializados para cada fonte:
- InfoMoney
- Valor Econômico
- Bloomberg Brasil
- E-Investidor (Estadão)
- Money Times

Execute com: python -m scripts.demo_all_sources
"""

from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.sources.pt import InfoMoneyScraper, ValorScraper, EInvestidorScraper, MoneyTimesScraper
from news_scraper.sources.en import BloombergScraper
from news_scraper.extract import extract_article_metadata


def demo_source(scraper_class, name: str, scraper: ProfessionalScraper):
    """Demonstra scraping de uma fonte específica."""
    print(f"\n{'=' * 70}")
    print(f"📰 {name}")
    print('=' * 70)
    
    source_scraper = scraper_class(scraper)
    
    # Coletar URLs
    print(f"\n1️⃣  Coletando URLs...")
    urls = source_scraper.get_latest_articles(limit=3)
    print(f"   ✓ {len(urls)} URLs coletadas")
    
    # Extrair metadados do primeiro artigo
    if urls:
        print(f"\n2️⃣  Extraindo metadados do primeiro artigo...")
        url = urls[0]
        print(f"   URL: {url[:80]}...")
        
        scraper.get_page(url, wait_time=3)
        article = extract_article_metadata(url, scraper.driver)
        
        print(f"\n   📄 Título: {article.title}")
        print(f"   📅 Data: {article.date_published}")
        print(f"   ✍️  Autor: {article.author or 'N/A'}")
        print(f"   📝 Texto: {len(article.text or '')} caracteres")
        print(f"   🏷️  Source: {article.source}")
        
        # Validação
        checks = {
            "Título extraído": article.title is not None,
            "Data extraída": article.date_published is not None,
            "Texto extraído": article.text is not None and len(article.text) > 100,
            "Source identificada": article.source is not None,
        }
        
        print("\n   ✅ Validação:")
        for check, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"      {status} {check}")


def main():
    """Executa demonstração para todas as fontes."""
    print("🚀 Demonstração de Scraping - Fontes de Notícias Financeiras")
    print("=" * 70)
    print("\nEste script demonstra a coleta e extração de metadados")
    print("das principais fontes de notícias financeiras do Brasil.")
    print("\nConfiguração: Selenium WebDriver (headless)")
    
    config = BrowserConfig(headless=True)
    
    with ProfessionalScraper(config) as scraper:
        # InfoMoney
        demo_source(InfoMoneyScraper, "InfoMoney", scraper)
        
        # Valor Econômico
        demo_source(ValorScraper, "Valor Econômico", scraper)
        
        # Bloomberg Brasil
        demo_source(BloombergScraper, "Bloomberg Brasil", scraper)
        
        # E-Investidor
        demo_source(EInvestidorScraper, "E-Investidor (Estadão)", scraper)
        
        # Money Times
        demo_source(MoneyTimesScraper, "Money Times", scraper)
    
    print("\n" + "=" * 70)
    print("✅ Demonstração concluída!")
    print("=" * 70)
    print("\n💡 Próximos passos:")
    print("   - Execute os testes: pytest tests/test_*_scraper.py")
    print("   - Use os scrapers em seus projetos")
    print("   - Ajuste os parâmetros conforme necessário")


if __name__ == "__main__":
    main()
