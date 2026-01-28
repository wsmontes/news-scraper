"""
Testes com benchmarks mínimos para validar scrapers operacionais.

Define critérios mínimos que cada scraper deve atender:
- Coleta de URLs: mínimo de artigos encontrados
- Extração de metadados: taxa mínima de sucesso
- Performance: tempo máximo de execução
- Qualidade: tamanho mínimo de texto
"""

import pytest
import time
from news_scraper.browser import ProfessionalScraper, BrowserConfig
from news_scraper.sources.pt import (
    InfoMoneyScraper,
    MoneyTimesScraper,
    ValorScraper,
    EInvestidorScraper,
)
from news_scraper.sources.en import (
    YahooFinanceUSScraper,
    BusinessInsiderScraper,
    BloombergScraper,
    InvestingComScraper,
    BloombergLatAmScraper,
    ReutersScraper,
    CNBCScraper,
    MarketWatchScraper,
)
from news_scraper.extract import extract_article_metadata


# Benchmarks mínimos para cada scraper
BENCHMARKS = {
    # PT Scrapers
    "infomoney": {
        "min_urls": 8,
        "min_metadata_success_rate": 0.66,
        "max_collection_time": 30,
        "max_extraction_time": 15,
        "min_text_length": 100,
        "required_fields": ["title", "date", "text", "source"],
    },
    "moneytimes": {
        "min_urls": 5,
        "min_metadata_success_rate": 0.66,
        "max_collection_time": 30,
        "max_extraction_time": 15,
        "min_text_length": 100,
        "required_fields": ["title", "date", "text", "source"],
    },
    "valor": {
        "min_urls": 8,
        "min_metadata_success_rate": 0.60,
        "max_collection_time": 45,
        "max_extraction_time": 20,
        "min_text_length": 100,
        "required_fields": ["title", "date", "text", "source"],
    },
    "einvestidor": {
        "min_urls": 5,
        "min_metadata_success_rate": 0.60,
        "max_collection_time": 45,
        "max_extraction_time": 20,
        "min_text_length": 100,
        "required_fields": ["title", "date", "text", "source"],
    },
    # EN Scrapers
    "yahoofinance": {
        "min_urls": 8,
        "min_metadata_success_rate": 0.60,
        "max_collection_time": 30,
        "max_extraction_time": 15,
        "min_text_length": 100,
        "required_fields": ["title", "date", "text", "source"],
    },
    "businessinsider": {
        "min_urls": 5,
        "min_metadata_success_rate": 0.50,
        "max_collection_time": 45,
        "max_extraction_time": 20,
        "min_text_length": 100,
        "required_fields": ["title", "date", "text", "source"],
    },
    "bloomberg": {
        "min_urls": 5,
        "min_metadata_success_rate": 0.50,
        "max_collection_time": 45,
        "max_extraction_time": 20,
        "min_text_length": 100,
        "required_fields": ["title", "date", "text", "source"],
    },
    "investing": {
        "min_urls": 5,
        "min_metadata_success_rate": 0.50,
        "max_collection_time": 40,
        "max_extraction_time": 15,
        "min_text_length": 100,
        "required_fields": ["title", "date", "text", "source"],
    },
    "bloomberg_latam": {
        "min_urls": 5,
        "min_metadata_success_rate": 0.50,
        "max_collection_time": 40,
        "max_extraction_time": 15,
        "min_text_length": 100,
        "required_fields": ["title", "date", "text", "source"],
    },
    "reuters": {
        "min_urls": 8,
        "min_metadata_success_rate": 0.60,
        "max_collection_time": 35,
        "max_extraction_time": 15,
        "min_text_length": 100,
        "required_fields": ["title", "date", "text", "source"],
    },
    "cnbc": {
        "min_urls": 8,
        "min_metadata_success_rate": 0.60,
        "max_collection_time": 35,
        "max_extraction_time": 15,
        "min_text_length": 100,
        "required_fields": ["title", "date", "text", "source"],
    },
    "marketwatch": {
        "min_urls": 8,
        "min_metadata_success_rate": 0.60,
        "max_collection_time": 35,
        "max_extraction_time": 15,
        "min_text_length": 100,
        "required_fields": ["title", "date", "text", "source"],
    },
}


def check_metadata_quality(metadata: dict, benchmarks: dict) -> dict:
    """
    Verifica qualidade dos metadados extraídos.
    
    Returns:
        Dict com resultado da validação
    """
    issues = []
    
    # Verificar campos obrigatórios
    for field in benchmarks["required_fields"]:
        if field not in metadata or not metadata[field]:
            issues.append(f"Campo '{field}' ausente ou vazio")
    
    # Verificar tamanho mínimo do texto
    if "text" in metadata:
        text_len = len(metadata["text"])
        if text_len < benchmarks["min_text_length"]:
            issues.append(f"Texto muito curto: {text_len} chars (mínimo: {benchmarks['min_text_length']})")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "metadata": metadata
    }


class TestInfoMoneyBenchmark:
    """Benchmarks para InfoMoney."""
    
    def test_url_collection_benchmark(self):
        """Testa se coleta mínimo de URLs no tempo esperado."""
        benchmarks = BENCHMARKS["infomoney"]
        
        config = BrowserConfig(headless=True)
        
        with ProfessionalScraper(config) as browser:
            scraper = InfoMoneyScraper(scraper=browser)
            
            start_time = time.time()
            urls = scraper.get_latest_articles(category="mercados", limit=10)
            elapsed = time.time() - start_time
        
        # Validações
        assert len(urls) >= benchmarks["min_urls"], \
            f"❌ FALHA: Coletou apenas {len(urls)} URLs (mínimo: {benchmarks['min_urls']})"
        
        assert elapsed <= benchmarks["max_collection_time"], \
            f"❌ FALHA: Coleta demorou {elapsed:.1f}s (máximo: {benchmarks['max_collection_time']}s)"
        
        print(f"\n✓ InfoMoney URL Collection: {len(urls)} URLs em {elapsed:.1f}s")
    
    def test_metadata_extraction_benchmark(self):
        """Testa taxa de sucesso na extração de metadados."""
        benchmarks = BENCHMARKS["infomoney"]
        config = BrowserConfig(headless=True)
        
        with ProfessionalScraper(config) as browser:
            scraper = InfoMoneyScraper(scraper=browser)
            urls = scraper.get_latest_articles(category="mercados", limit=5)
            
            results = []
            total_time = 0
            
            for url in urls:
                start_time = time.time()
                metadata = extract_article_metadata(url, browser)
                elapsed = time.time() - start_time
                total_time += elapsed
                
                validation = check_metadata_quality(metadata, benchmarks)
                results.append({
                    "url": url,
                    "elapsed": elapsed,
                    "validation": validation
                })
                
                # Verificar tempo máximo por artigo
                assert elapsed <= benchmarks["max_extraction_time"], \
                    f"❌ FALHA: Extração demorou {elapsed:.1f}s (máximo: {benchmarks['max_extraction_time']}s)"
        
        # Calcular taxa de sucesso
        successful = sum(1 for r in results if r["validation"]["valid"])
        success_rate = successful / len(results)
        
        # Validação final
        assert success_rate >= benchmarks["min_metadata_success_rate"], \
            f"❌ FALHA: Taxa de sucesso {success_rate:.1%} abaixo do mínimo ({benchmarks['min_metadata_success_rate']:.1%})"
        
        # Relatório
        print(f"\n✓ InfoMoney Metadata Extraction:")
        print(f"  - Taxa de sucesso: {success_rate:.1%}")
        print(f"  - Tempo médio: {total_time/len(results):.1f}s por artigo")
        print(f"  - Artigos válidos: {successful}/{len(results)}")
        
        # Mostrar problemas se houver
        for r in results:
            if not r["validation"]["valid"]:
                print(f"\n  ⚠️ Problemas em {r['url']}:")
                for issue in r["validation"]["issues"]:
                    print(f"     - {issue}")


class TestMoneyTimesBenchmark:
    """Benchmarks para Money Times."""
    
    def test_url_collection_benchmark(self):
        """Testa se coleta mínimo de URLs no tempo esperado."""
        benchmarks = BENCHMARKS["moneytimes"]
        
        config = BrowserConfig(headless=True)
        
        with ProfessionalScraper(config) as browser:
            scraper = MoneyTimesScraper(scraper=browser)
            
            start_time = time.time()
            urls = scraper.get_latest_articles(limit=10)
            elapsed = time.time() - start_time
        
        assert len(urls) >= benchmarks["min_urls"], \
            f"❌ FALHA: Coletou apenas {len(urls)} URLs (mínimo: {benchmarks['min_urls']})"
        
        assert elapsed <= benchmarks["max_collection_time"], \
            f"❌ FALHA: Coleta demorou {elapsed:.1f}s (máximo: {benchmarks['max_collection_time']}s)"
        
        print(f"\n✓ Money Times URL Collection: {len(urls)} URLs em {elapsed:.1f}s")


# Remover fixtures não utilizadas e outras classes por enquanto
@pytest.fixture(scope="module")
def benchmark_config():
    """Configuração padrão para benchmarks."""
    return BrowserConfig(headless=True)


class TestValorBenchmark:
    """Benchmarks para Valor Econômico."""
    
    def test_url_collection_benchmark(self):
        """Testa se coleta mínimo de URLs no tempo esperado."""
        benchmarks = BENCHMARKS["valor"]
        
        config = BrowserConfig(headless=True)
        
        with ProfessionalScraper(config) as browser:
            scraper = ValorScraper(scraper=browser)
            
            start_time = time.time()
            urls = scraper.get_latest_articles(limit=15)
            elapsed = time.time() - start_time
        
        assert len(urls) >= benchmarks["min_urls"], \
            f"❌ FALHA: Coletou apenas {len(urls)} URLs (mínimo: {benchmarks['min_urls']})"
        
        assert elapsed <= benchmarks["max_collection_time"], \
            f"❌ FALHA: Coleta demorou {elapsed:.1f}s (máximo: {benchmarks['max_collection_time']}s)"
        
        print(f"\n✓ Valor URL Collection: {len(urls)} URLs em {elapsed:.1f}s")
    
    def test_metadata_extraction_benchmark(self):
        """Testa taxa de sucesso na extração de metadados."""
        benchmarks = BENCHMARKS["valor"]
        
        config = BrowserConfig(headless=True)
        
        with ProfessionalScraper(config) as browser:
            scraper = ValorScraper(scraper=browser)
            urls = scraper.get_latest_articles(limit=5)
            
            if not urls:
                pytest.skip("Nenhuma URL coletada")
            
            results = []
            for url in urls[:3]:  # Testar apenas 3 para não demorar muito
                start_time = time.time()
                metadata = extract_article_metadata(url, browser.driver)
                elapsed = time.time() - start_time
                
                quality = check_metadata_quality(metadata, benchmarks)
                results.append({
                    "url": url,
                    "elapsed": elapsed,
                    "validation": quality,
                })
        
        # Calcular taxa de sucesso
        valid_count = sum(1 for r in results if r["validation"]["valid"])
        success_rate = valid_count / len(results)
        
        assert success_rate >= benchmarks["min_metadata_success_rate"], \
            f"❌ FALHA: Taxa de sucesso {success_rate:.1%} < {benchmarks['min_metadata_success_rate']:.1%}"
        
        print(f"\n✓ Valor Metadata: {success_rate:.1%} de sucesso ({valid_count}/{len(results)})")
        
        for r in results:
            if not r["validation"]["valid"]:
                print(f"\n  ⚠️ Problemas em {r['url']}:")
                for issue in r["validation"]["issues"]:
                    print(f"     - {issue}")
    
    def test_content_quality_benchmark(self):
        """Testa qualidade do conteúdo extraído."""
        benchmarks = BENCHMARKS["valor"]
        
        config = BrowserConfig(headless=True)
        
        with ProfessionalScraper(config) as browser:
            scraper = ValorScraper(scraper=browser)
            urls = scraper.get_latest_articles(limit=3)
            
            if not urls:
                pytest.skip("Nenhuma URL coletada")
            
            url = urls[0]
            metadata = extract_article_metadata(url, browser.driver)
            
            text = metadata.get("text", "")
            
            assert len(text) >= benchmarks["min_text_length"], \
                f"❌ FALHA: Texto muito curto ({len(text)} chars < {benchmarks['min_text_length']})"
            
            print(f"\n✓ Valor Content Quality: {len(text)} caracteres extraídos")


class TestEInvestidorBenchmark:
    """Benchmarks para E-Investidor."""
    
    def test_url_collection_benchmark(self):
        """Testa se coleta mínimo de URLs no tempo esperado."""
        benchmarks = BENCHMARKS["einvestidor"]
        
        config = BrowserConfig(headless=True)
        
        with ProfessionalScraper(config) as browser:
            scraper = EInvestidorScraper(scraper=browser)
            
            start_time = time.time()
            urls = scraper.get_latest_articles(limit=10)
            elapsed = time.time() - start_time
        
        assert len(urls) >= benchmarks["min_urls"], \
            f"❌ FALHA: Coletou apenas {len(urls)} URLs (mínimo: {benchmarks['min_urls']})"
        
        assert elapsed <= benchmarks["max_collection_time"], \
            f"❌ FALHA: Coleta demorou {elapsed:.1f}s (máximo: {benchmarks['max_collection_time']}s)"
        
        print(f"\n✓ E-Investidor URL Collection: {len(urls)} URLs em {elapsed:.1f}s")
    
    def test_metadata_extraction_benchmark(self):
        """Testa taxa de sucesso na extração de metadados."""
        benchmarks = BENCHMARKS["einvestidor"]
        
        config = BrowserConfig(headless=True)
        
        with ProfessionalScraper(config) as browser:
            scraper = EInvestidorScraper(scraper=browser)
            urls = scraper.get_latest_articles(limit=5)
            
            if not urls:
                pytest.skip("Nenhuma URL coletada")
            
            results = []
            for url in urls[:3]:  # Testar apenas 3
                start_time = time.time()
                metadata = extract_article_metadata(url, browser.driver)
                elapsed = time.time() - start_time
                
                quality = check_metadata_quality(metadata, benchmarks)
                results.append({
                    "url": url,
                    "elapsed": elapsed,
                    "validation": quality,
                })
        
        # Calcular taxa de sucesso
        valid_count = sum(1 for r in results if r["validation"]["valid"])
        success_rate = valid_count / len(results)
        
        assert success_rate >= benchmarks["min_metadata_success_rate"], \
            f"❌ FALHA: Taxa de sucesso {success_rate:.1%} < {benchmarks['min_metadata_success_rate']:.1%}"
        
        print(f"\n✓ E-Investidor Metadata: {success_rate:.1%} de sucesso ({valid_count}/{len(results)})")
        
        for r in results:
            if not r["validation"]["valid"]:
                print(f"\n  ⚠️ Problemas em {r['url']}:")
                for issue in r["validation"]["issues"]:
                    print(f"     - {issue}")
    
    def test_content_quality_benchmark(self):
        """Testa qualidade do conteúdo extraído."""
        benchmarks = BENCHMARKS["einvestidor"]
        
        config = BrowserConfig(headless=True)
        
        with ProfessionalScraper(config) as browser:
            scraper = EInvestidorScraper(scraper=browser)
            urls = scraper.get_latest_articles(limit=3)
            
            if not urls:
                pytest.skip("Nenhuma URL coletada")
            
            url = urls[0]
            metadata = extract_article_metadata(url, browser.driver)
            
            text = metadata.get("text", "")
            
            assert len(text) >= benchmarks["min_text_length"], \
                f"❌ FALHA: Texto muito curto ({len(text)} chars < {benchmarks['min_text_length']})"
            
            print(f"\n✓ E-Investidor Content Quality: {len(text)} caracteres extraídos")


# ========== EN SCRAPERS BENCHMARKS ==========

class TestYahooFinanceBenchmark:
    """Benchmarks para Yahoo Finance US."""
    
    def test_url_collection_benchmark(self):
        """Testa coleta de URLs."""
        benchmarks = BENCHMARKS["yahoofinance"]
        
        config = BrowserConfig(headless=True)
        with ProfessionalScraper(config) as browser:
            scraper = YahooFinanceUSScraper(scraper=browser)
            
            start_time = time.time()
            urls = scraper.get_latest_articles(limit=15)
            elapsed = time.time() - start_time
        
        assert len(urls) >= benchmarks["min_urls"], \
            f"❌ Coletou {len(urls)}/{benchmarks['min_urls']} URLs"
        assert elapsed <= benchmarks["max_collection_time"], \
            f"❌ Demorou {elapsed:.1f}s (max {benchmarks['max_collection_time']}s)"
        
        print(f"\n✓ Yahoo Finance: {len(urls)} URLs em {elapsed:.1f}s")


class TestBusinessInsiderBenchmark:
    """Benchmarks para Business Insider."""
    
    def test_url_collection_benchmark(self):
        """Testa coleta de URLs."""
        benchmarks = BENCHMARKS["businessinsider"]
        
        config = BrowserConfig(headless=True)
        with ProfessionalScraper(config) as browser:
            scraper = BusinessInsiderScraper(scraper=browser)
            
            start_time = time.time()
            urls = scraper.get_latest_articles(limit=10)
            elapsed = time.time() - start_time
        
        assert len(urls) >= benchmarks["min_urls"], \
            f"❌ Coletou {len(urls)}/{benchmarks['min_urls']} URLs"
        assert elapsed <= benchmarks["max_collection_time"], \
            f"❌ Demorou {elapsed:.1f}s (max {benchmarks['max_collection_time']}s)"
        
        print(f"\n✓ Business Insider: {len(urls)} URLs em {elapsed:.1f}s")


class TestBloombergBenchmark:
    """Benchmarks para Bloomberg."""
    
    def test_url_collection_benchmark(self):
        """Testa coleta de URLs."""
        benchmarks = BENCHMARKS["bloomberg"]
        
        config = BrowserConfig(headless=True)
        with ProfessionalScraper(config) as browser:
            scraper = BloombergScraper(scraper=browser)
            
            start_time = time.time()
            urls = scraper.get_latest_articles(limit=10)
            elapsed = time.time() - start_time
        
        assert len(urls) >= benchmarks["min_urls"], \
            f"❌ Coletou {len(urls)}/{benchmarks['min_urls']} URLs"
        assert elapsed <= benchmarks["max_collection_time"], \
            f"❌ Demorou {elapsed:.1f}s (max {benchmarks['max_collection_time']}s)"
        
        print(f"\n✓ Bloomberg: {len(urls)} URLs em {elapsed:.1f}s")


class TestInvestingComBenchmark:
    """Benchmarks para Investing.com."""
    
    def test_url_collection_benchmark(self):
        """Testa coleta de URLs."""
        benchmarks = BENCHMARKS["investing"]
        
        config = BrowserConfig(headless=True)
        with ProfessionalScraper(config) as browser:
            scraper = InvestingComScraper(scraper=browser)
            
            start_time = time.time()
            urls = scraper.get_latest_articles(limit=10)
            elapsed = time.time() - start_time
        
        assert len(urls) >= benchmarks["min_urls"], \
            f"❌ Coletou {len(urls)}/{benchmarks['min_urls']} URLs"
        assert elapsed <= benchmarks["max_collection_time"], \
            f"❌ Demorou {elapsed:.1f}s (max {benchmarks['max_collection_time']}s)"
        
        print(f"\n✓ Investing.com: {len(urls)} URLs em {elapsed:.1f}s")


class TestBloombergLatAmBenchmark:
    """Benchmarks para Bloomberg LatAm."""
    
    def test_url_collection_benchmark(self):
        """Testa coleta de URLs."""
        benchmarks = BENCHMARKS["bloomberg_latam"]
        
        config = BrowserConfig(headless=True)
        with ProfessionalScraper(config) as browser:
            scraper = BloombergLatAmScraper(scraper=browser)
            
            start_time = time.time()
            urls = scraper.get_latest_articles(limit=10)
            elapsed = time.time() - start_time
        
        assert len(urls) >= benchmarks["min_urls"], \
            f"❌ Coletou {len(urls)}/{benchmarks['min_urls']} URLs"
        assert elapsed <= benchmarks["max_collection_time"], \
            f"❌ Demorou {elapsed:.1f}s (max {benchmarks['max_collection_time']}s)"
        
        print(f"\n✓ Bloomberg LatAm: {len(urls)} URLs em {elapsed:.1f}s")


class TestReutersBenchmark:
    """Benchmarks para Reuters."""
    
    def test_url_collection_benchmark(self):
        """Testa coleta de URLs."""
        benchmarks = BENCHMARKS["reuters"]
        
        config = BrowserConfig(headless=True)
        with ProfessionalScraper(config) as browser:
            scraper = ReutersScraper(scraper=browser)
            
            start_time = time.time()
            urls = scraper.get_latest_articles(limit=15)
            elapsed = time.time() - start_time
        
        assert len(urls) >= benchmarks["min_urls"], \
            f"❌ Coletou {len(urls)}/{benchmarks['min_urls']} URLs"
        assert elapsed <= benchmarks["max_collection_time"], \
            f"❌ Demorou {elapsed:.1f}s (max {benchmarks['max_collection_time']}s)"
        
        print(f"\n✓ Reuters: {len(urls)} URLs em {elapsed:.1f}s")


class TestCNBCBenchmark:
    """Benchmarks para CNBC."""
    
    def test_url_collection_benchmark(self):
        """Testa coleta de URLs."""
        benchmarks = BENCHMARKS["cnbc"]
        
        config = BrowserConfig(headless=True)
        with ProfessionalScraper(config) as browser:
            scraper = CNBCScraper(scraper=browser)
            
            start_time = time.time()
            urls = scraper.get_latest_articles(limit=15)
            elapsed = time.time() - start_time
        
        assert len(urls) >= benchmarks["min_urls"], \
            f"❌ Coletou {len(urls)}/{benchmarks['min_urls']} URLs"
        assert elapsed <= benchmarks["max_collection_time"], \
            f"❌ Demorou {elapsed:.1f}s (max {benchmarks['max_collection_time']}s)"
        
        print(f"\n✓ CNBC: {len(urls)} URLs em {elapsed:.1f}s")


class TestMarketWatchBenchmark:
    """Benchmarks para MarketWatch."""
    
    def test_url_collection_benchmark(self):
        """Testa coleta de URLs."""
        benchmarks = BENCHMARKS["marketwatch"]
        
        config = BrowserConfig(headless=True)
        with ProfessionalScraper(config) as browser:
            scraper = MarketWatchScraper(scraper=browser)
            
            start_time = time.time()
            urls = scraper.get_latest_articles(limit=15)
            elapsed = time.time() - start_time
        
        assert len(urls) >= benchmarks["min_urls"], \
            f"❌ Coletou {len(urls)}/{benchmarks['min_urls']} URLs"
        assert elapsed <= benchmarks["max_collection_time"], \
            f"❌ Demorou {elapsed:.1f}s (max {benchmarks['max_collection_time']}s)"
        
        print(f"\n✓ MarketWatch: {len(urls)} URLs em {elapsed:.1f}s")
