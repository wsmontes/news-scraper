"""
Testes de qualidade para as fontes prioritárias.

Valida:
1. Taxa de sucesso na coleta (>= 50% das URLs solicitadas)
2. Qualidade das URLs (validação de formato)
3. Performance (tempo máximo)
4. Resiliência (não falha em exceção simples)
"""

import pytest
from datetime import datetime
import time
from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.sources.en import (
    YahooFinanceUSScraper,
    BusinessInsiderScraper,
    InvestingComScraper,
    BloombergLatAmScraper,
)


@pytest.fixture(scope="module")
def browser():
    """Browser compartilhado para todos os testes."""
    config = BrowserConfig(headless=True)
    scraper = ProfessionalScraper(config)
    scraper.start()
    yield scraper
    scraper.stop()


class TestYahooFinanceUSQuality:
    """Testes de qualidade do Yahoo Finance US."""
    
    def test_collects_minimum_urls(self, browser):
        """Deve coletar pelo menos 50% das URLs solicitadas."""
        scraper = YahooFinanceUSScraper(browser)
        urls = scraper.get_latest_articles(category="stock-market-news", limit=20)
        
        # Taxa mínima de sucesso: 50%
        assert len(urls) >= 10, f"Coletou apenas {len(urls)}/20 URLs (< 50% mínimo)"
    
    def test_url_format_validation(self, browser):
        """URLs devem ser válidas e do domínio correto."""
        scraper = YahooFinanceUSScraper(browser)
        urls = scraper.get_latest_articles(category="latest-news", limit=10)
        
        assert len(urls) > 0, "Nenhuma URL coletada"
        
        for url in urls:
            assert url.startswith("http"), f"URL inválida (sem http): {url}"
            assert "finance.yahoo.com" in url, f"URL de domínio incorreto: {url}"
            assert len(url) > 30, f"URL muito curta: {url}"
    
    def test_performance(self, browser):
        """Coleta deve completar em tempo razoável."""
        scraper = YahooFinanceUSScraper(browser)
        
        start = time.time()
        urls = scraper.get_latest_articles(category="stock-market-news", limit=20)
        elapsed = time.time() - start
        
        # Máximo 60s para coletar 20 URLs
        assert elapsed < 60, f"Coleta muito lenta: {elapsed:.2f}s (máx 60s)"
        assert len(urls) > 0, "Timeout sem coletar URLs"
    
    def test_multiple_categories(self, browser):
        """Diferentes categorias devem funcionar."""
        scraper = YahooFinanceUSScraper(browser)
        
        categories = ["stock-market-news", "latest-news"]
        results = {}
        
        for cat in categories:
            urls = scraper.get_latest_articles(category=cat, limit=10)
            results[cat] = len(urls)
        
        # Pelo menos 1 categoria deve ter URLs
        working_cats = sum(1 for count in results.values() if count > 0)
        assert working_cats >= 1, f"Nenhuma categoria funcionou: {results}"


class TestBusinessInsiderQuality:
    """Testes de qualidade do Business Insider."""
    
    def test_collects_minimum_urls(self, browser):
        """Deve coletar pelo menos 50% das URLs solicitadas."""
        scraper = BusinessInsiderScraper(browser)
        urls = scraper.get_latest_articles(category="main", limit=20)
        
        # Taxa mínima de sucesso: 50%
        assert len(urls) >= 10, f"Coletou apenas {len(urls)}/20 URLs (< 50% mínimo)"
    
    def test_url_format_validation(self, browser):
        """URLs devem ser válidas e do domínio correto."""
        scraper = BusinessInsiderScraper(browser)
        urls = scraper.get_latest_articles(category="markets", limit=10)
        
        assert len(urls) > 0, "Nenhuma URL coletada"
        
        for url in urls:
            assert url.startswith("http"), f"URL inválida (sem http): {url}"
            assert "businessinsider.com" in url, f"URL de domínio incorreto: {url}"
            # Business Insider usa slugs longos
            assert len(url) > 40, f"URL muito curta: {url}"
    
    def test_handles_paywall_gracefully(self, browser):
        """Deve lidar com paywall sem falhar."""
        scraper = BusinessInsiderScraper(browser)
        
        # Não deve lançar exceção mesmo com paywall
        try:
            urls = scraper.get_latest_articles(category="finance", limit=10)
            assert isinstance(urls, list), "Deve retornar lista mesmo com paywall"
        except Exception as e:
            pytest.fail(f"Não deve falhar com exceção: {e}")


class TestInvestingComQuality:
    """Testes de qualidade do Investing.com."""
    
    def test_collects_minimum_urls(self, browser):
        """Deve coletar pelo menos 50% das URLs solicitadas."""
        scraper = InvestingComScraper(browser)
        urls = scraper.get_latest_articles(category="news", limit=20)
        
        # Taxa mínima de sucesso: 50%
        assert len(urls) >= 10, f"Coletou apenas {len(urls)}/20 URLs (< 50% mínimo)"
    
    def test_url_format_validation(self, browser):
        """URLs devem ser válidas e do domínio correto."""
        scraper = InvestingComScraper(browser)
        urls = scraper.get_latest_articles(category="stock-market-news", limit=10)
        
        assert len(urls) > 0, "Nenhuma URL coletada"
        
        for url in urls:
            assert url.startswith("http"), f"URL inválida (sem http): {url}"
            assert "investing.com" in url, f"URL de domínio incorreto: {url}"
            assert "/news/" in url, f"URL não é de notícia: {url}"
    
    def test_article_id_validation(self, browser):
        """URLs devem ter ID de artigo (numérico)."""
        scraper = InvestingComScraper(browser)
        urls = scraper.get_latest_articles(category="economy", limit=10)
        
        assert len(urls) > 0, "Nenhuma URL coletada"
        
        for url in urls:
            # Investing.com usa IDs numéricos no final das URLs
            url_parts = url.split("/")[-1]
            has_digits = any(char.isdigit() for char in url_parts)
            assert has_digits, f"URL sem ID numérico: {url}"


class TestBloombergLatAmQuality:
    """Testes de qualidade do Bloomberg Latin America."""
    
    def test_collects_minimum_urls(self, browser):
        """Deve coletar pelo menos 50% das URLs solicitadas."""
        scraper = BloombergLatAmScraper(browser)
        urls = scraper.get_latest_articles(category="latinamerica", limit=20)
        
        # Taxa mínima de sucesso: 50%
        assert len(urls) >= 10, f"Coletou apenas {len(urls)}/20 URLs (< 50% mínimo)"
    
    def test_url_format_validation(self, browser):
        """URLs devem ser válidas e do domínio correto."""
        scraper = BloombergLatAmScraper(browser)
        urls = scraper.get_latest_articles(category="latinamerica", limit=10)
        
        assert len(urls) > 0, "Nenhuma URL coletada"
        
        for url in urls:
            assert url.startswith("http"), f"URL inválida (sem http): {url}"
            assert "bloomberg.com" in url, f"URL de domínio incorreto: {url}"
            # Bloomberg usa padrão /news/articles/ ou /articles/
            assert "/articles/" in url or "/news/" in url, f"URL não é artigo: {url}"
    
    def test_no_query_params(self, browser):
        """URLs devem estar limpas (sem query params)."""
        scraper = BloombergLatAmScraper(browser)
        urls = scraper.get_latest_articles(category="latinamerica", limit=10)
        
        assert len(urls) > 0, "Nenhuma URL coletada"
        
        for url in urls:
            assert "?" not in url, f"URL com query params: {url}"
            assert "#" not in url, f"URL com fragment: {url}"


class TestPrioritySourcesComparison:
    """Testes comparativos entre todas as fontes prioritárias."""
    
    def test_all_sources_functional(self, browser):
        """Todas as fontes devem coletar pelo menos algumas URLs."""
        sources = [
            (YahooFinanceUSScraper, "stock-market-news"),
            (BusinessInsiderScraper, "main"),
            (InvestingComScraper, "news"),
            (BloombergLatAmScraper, "latinamerica"),
        ]
        
        results = {}
        for scraper_class, category in sources:
            scraper = scraper_class(browser)
            urls = scraper.get_latest_articles(category=category, limit=10)
            results[scraper_class.__name__] = len(urls)
        
        # Todas as fontes devem coletar pelo menos 3 URLs
        failed_sources = [name for name, count in results.items() if count < 3]
        
        assert len(failed_sources) == 0, f"Fontes falharam (< 3 URLs): {failed_sources}\nResultados: {results}"
    
    def test_performance_comparison(self, browser):
        """Compara performance entre fontes."""
        sources = [
            (YahooFinanceUSScraper, "stock-market-news"),
            (BusinessInsiderScraper, "main"),
            (InvestingComScraper, "news"),
            (BloombergLatAmScraper, "latinamerica"),
        ]
        
        times = {}
        for scraper_class, category in sources:
            scraper = scraper_class(browser)
            
            start = time.time()
            urls = scraper.get_latest_articles(category=category, limit=10)
            elapsed = time.time() - start
            
            times[scraper_class.__name__] = {
                "time": elapsed,
                "urls": len(urls),
                "urls_per_second": len(urls) / elapsed if elapsed > 0 else 0
            }
        
        # Nenhuma fonte deve levar mais de 60s para 10 URLs
        slow_sources = [name for name, data in times.items() if data["time"] > 60]
        
        assert len(slow_sources) == 0, f"Fontes muito lentas (> 60s): {slow_sources}\nTempos: {times}"
    
    def test_success_rate_statistics(self, browser):
        """Calcula e valida taxa de sucesso geral."""
        sources = [
            (YahooFinanceUSScraper, "stock-market-news", "yahoofinance"),
            (BusinessInsiderScraper, "main", "businessinsider"),
            (InvestingComScraper, "news", "investing"),
            (BloombergLatAmScraper, "latinamerica", "bloomberg-latam"),
        ]
        
        total_requested = 0
        total_collected = 0
        
        for scraper_class, category, name in sources:
            scraper = scraper_class(browser)
            requested = 15
            urls = scraper.get_latest_articles(category=category, limit=requested)
            collected = len(urls)
            
            total_requested += requested
            total_collected += collected
            
            print(f"\n{name}: {collected}/{requested} URLs ({(collected/requested)*100:.1f}%)")
        
        overall_rate = (total_collected / total_requested) * 100
        print(f"\nTaxa geral: {total_collected}/{total_requested} ({overall_rate:.1f}%)")
        
        # Taxa mínima geral: 40% (considerando possíveis variações de site)
        assert overall_rate >= 40, f"Taxa de sucesso geral muito baixa: {overall_rate:.1f}% (mínimo 40%)"


@pytest.mark.slow
class TestPrioritySourcesUnderLoad:
    """Testes de stress para fontes prioritárias."""
    
    def test_high_volume_collection(self, browser):
        """Testa coleta de alto volume."""
        scraper = YahooFinanceUSScraper(browser)
        
        # Coletar 50 URLs (acima do padrão de 20)
        urls = scraper.get_latest_articles(category="stock-market-news", limit=50)
        
        # Deve conseguir pelo menos 30 URLs (60%)
        assert len(urls) >= 30, f"Alto volume falhou: {len(urls)}/50 URLs"
    
    def test_repeated_collections(self, browser):
        """Testa múltiplas coletas sequenciais."""
        scraper = InvestingComScraper(browser)
        
        collections = []
        for i in range(3):
            urls = scraper.get_latest_articles(category="news", limit=10)
            collections.append(len(urls))
        
        # Todas as coletas devem ter pelo menos 5 URLs
        failed_collections = [i for i, count in enumerate(collections) if count < 5]
        
        assert len(failed_collections) == 0, f"Coletas falharam: {failed_collections}\nResultados: {collections}"
