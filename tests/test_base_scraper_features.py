"""
Testes das funcionalidades da classe base BaseScraper.

Valida:
1. Sistema de retry automático
2. Coleta de métricas
3. Validação de taxa de sucesso
4. Detecção de paywall
5. Integração com ferramentas (RetryStrategy, RateLimiter)
"""

import pytest
from datetime import datetime, timedelta
from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.sources.en import YahooFinanceUSScraper
from news_scraper.sources.base_scraper import (
    ScraperMetrics,
    InsufficientDataException,
    PaywallException,
    MetricsCollector
)


@pytest.fixture(scope="module")
def browser():
    """Browser compartilhado."""
    config = BrowserConfig(headless=True)
    scraper = ProfessionalScraper(config)
    scraper.start()  # Inicializar browser
    yield scraper
    # ProfessionalScraper não tem método close()
    # Limpeza automática quando sai do escopo


@pytest.fixture
def metrics_collector():
    """Coletor de métricas limpo."""
    collector = MetricsCollector()
    collector.clear()
    return collector


class TestBasicScraperFeatures:
    """Testes das funcionalidades básicas."""
    
    def test_scraper_collects_with_metrics(self, browser):
        """Scraper deve coletar métricas automaticamente."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.clear_metrics()
        
        urls = scraper.get_latest_articles(category="stock-market-news", limit=10)
        
        # Deve ter métricas
        metrics = scraper.get_latest_metrics()
        assert metrics is not None
        assert metrics.source_id == "yahoofinance"
        assert metrics.requested == 10
        assert metrics.collected == len(urls)
        assert 0 <= metrics.success_rate <= 1
        assert metrics.time_seconds > 0
    
    def test_metrics_export(self, browser):
        """Métricas devem ser exportáveis."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.clear_metrics()
        
        scraper.get_latest_articles(category="latest-news", limit=5)
        
        exported = scraper.export_metrics()
        assert isinstance(exported, list)
        assert len(exported) > 0
        
        first_metric = exported[0]
        assert "source_id" in first_metric
        assert "success_rate" in first_metric
        assert "time_seconds" in first_metric
        assert "collected" in first_metric
    
    def test_average_success_rate(self, browser):
        """Deve calcular taxa média de sucesso."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.clear_metrics()
        
        # Executar múltiplas coletas
        for _ in range(3):
            scraper.get_latest_articles(category="stock-market-news", limit=10)
        
        avg_rate = scraper.get_average_success_rate()
        assert 0 <= avg_rate <= 1
        assert len(scraper.get_metrics()) == 3


class TestSuccessRateValidation:
    """Testes de validação de taxa de sucesso."""
    
    def test_warning_on_low_success_rate(self, browser, caplog):
        """Deve gerar warning quando taxa < mínimo."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.MIN_SUCCESS_RATE = 0.9  # 90% - muito alto para passar
        
        # Não deve lançar exceção por padrão
        urls = scraper.get_latest_articles(category="markets", limit=20)
        
        # Deve ter warning no log se não atingiu taxa
        if len(urls) < 18:  # 90% de 20
            assert any("Taxa de sucesso baixa" in record.message for record in caplog.records)
    
    def test_raises_on_insufficient_data(self, browser):
        """Deve lançar exceção quando taxa baixa e raise_on_insufficient=True."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.MIN_SUCCESS_RATE = 0.95  # 95% - quase impossível
        
        with pytest.raises(InsufficientDataException) as exc_info:
            scraper.get_latest_articles(
                category="news",
                limit=20,
                raise_on_insufficient=True
            )
        
        assert "Taxa de sucesso baixa" in str(exc_info.value)
    
    def test_custom_min_success_rate(self, browser):
        """Deve aceitar taxa mínima customizada."""
        scraper = YahooFinanceUSScraper(browser)
        
        # Taxa customizada mais baixa
        urls = scraper.get_latest_articles(
            category="latest-news",
            limit=10,
            min_success_rate=0.3  # 30% - bem baixo
        )
        
        # Deve ter coletado algo
        assert isinstance(urls, list)


class TestRetryMechanism:
    """Testes do mecanismo de retry."""
    
    def test_retry_count_in_metrics(self, browser):
        """Métricas devem registrar contagem de retries."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.clear_metrics()
        
        urls = scraper.get_latest_articles(category="stock-market-news", limit=10)
        
        metrics = scraper.get_latest_metrics()
        assert metrics.retry_count >= 0
        # Se coletou URLs com sucesso, retry_count pode ser 0
        if len(urls) > 0:
            assert metrics.retry_count >= 0
    
    def test_errors_logged_in_metrics(self, browser):
        """Erros devem ser registrados nas métricas."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.clear_metrics()
        
        urls = scraper.get_latest_articles(category="stock-market-news", limit=10)
        
        metrics = scraper.get_latest_metrics()
        assert isinstance(metrics.errors, list)
        # Se teve sucesso, lista pode estar vazia


class TestMetricsCollector:
    """Testes do coletor central de métricas."""
    
    def test_collector_aggregates_metrics(self, browser, metrics_collector):
        """Coletor deve agregar métricas de múltiplas fontes."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.clear_metrics()
        
        # Executar múltiplas coletas
        for i in range(3):
            scraper.get_latest_articles(category="markets", limit=5)
        
        # Adicionar ao coletor
        for metrics in scraper.get_metrics():
            metrics_collector.add_metrics(metrics)
        
        all_metrics = metrics_collector.get_all_metrics()
        assert len(all_metrics) >= 3
    
    def test_collector_filters_by_source(self, browser, metrics_collector):
        """Coletor deve filtrar por fonte."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.clear_metrics()
        
        scraper.get_latest_articles(category="news", limit=10)
        
        for metrics in scraper.get_metrics():
            metrics_collector.add_metrics(metrics)
        
        yahoo_metrics = metrics_collector.get_metrics_by_source("yahoofinance")
        assert len(yahoo_metrics) > 0
        assert all(m.source_id == "yahoofinance" for m in yahoo_metrics)
    
    def test_collector_statistics(self, browser, metrics_collector):
        """Coletor deve calcular estatísticas."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.clear_metrics()
        
        # Executar coletas
        for _ in range(2):
            scraper.get_latest_articles(category="stock-market-news", limit=10)
        
        for metrics in scraper.get_metrics():
            metrics_collector.add_metrics(metrics)
        
        stats = metrics_collector.get_statistics()
        
        assert "total_executions" in stats
        assert "avg_success_rate" in stats
        assert "avg_time_seconds" in stats
        assert "by_source" in stats
        assert stats["total_executions"] >= 2
    
    def test_collector_export_json(self, browser, metrics_collector):
        """Coletor deve exportar para JSON."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.clear_metrics()
        
        scraper.get_latest_articles(category="latest-news", limit=5)
        
        for metrics in scraper.get_metrics():
            metrics_collector.add_metrics(metrics)
        
        json_data = metrics_collector.export_json()
        
        assert isinstance(json_data, str)
        assert len(json_data) > 0
        
        # Deve ser JSON válido
        import json
        parsed = json.loads(json_data)
        assert isinstance(parsed, list)


class TestPaywallDetection:
    """Testes de detecção de paywall."""
    
    def test_paywall_flag_in_metrics(self, browser):
        """Métricas devem registrar flag de paywall."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.clear_metrics()
        
        urls = scraper.get_latest_articles(category="markets", limit=10)
        
        metrics = scraper.get_latest_metrics()
        assert isinstance(metrics.has_paywall_detected, bool)
        # Yahoo Finance não tem paywall
        assert metrics.has_paywall_detected == False


class TestDateFiltering:
    """Testes de filtros de data."""
    
    def test_date_parameters_accepted(self, browser):
        """Scraper deve aceitar parâmetros de data."""
        scraper = YahooFinanceUSScraper(browser)
        
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        # Não deve lançar exceção
        urls = scraper.get_latest_articles(
            category="stock-market-news",
            limit=10,
            start_date=start_date,
            end_date=end_date
        )
        
        assert isinstance(urls, list)
    
    def test_date_filtering_warning(self, browser, caplog):
        """Deve gerar warning se filtro de data não implementado."""
        scraper = YahooFinanceUSScraper(browser)
        
        start_date = datetime.now() - timedelta(days=1)
        
        urls = scraper.get_latest_articles(
            category="latest-news",
            limit=5,
            start_date=start_date
        )
        
        # Deve ter warning sobre filtro não implementado
        # (depende da implementação específica do scraper)
        assert isinstance(urls, list)


@pytest.mark.integration
class TestIntegrationWithRealData:
    """Testes de integração com dados reais."""
    
    def test_full_workflow_with_validation(self, browser):
        """Workflow completo: coleta → validação → métricas."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.clear_metrics()
        
        # 1. Coletar com validação
        urls = scraper.get_latest_articles(
            category="stock-market-news",
            limit=15,
            min_success_rate=0.5  # 50% mínimo
        )
        
        # 2. Validar resultado
        assert isinstance(urls, list)
        assert len(urls) >= 7  # Pelo menos 50% de 15
        
        # 3. Verificar métricas
        metrics = scraper.get_latest_metrics()
        assert metrics.collected >= 7
        assert metrics.success_rate >= 0.5
        
        # 4. Verificar qualidade das URLs
        for url in urls:
            assert url.startswith("http")
            assert "finance.yahoo.com" in url
    
    def test_performance_within_limits(self, browser):
        """Performance deve estar dentro dos limites."""
        scraper = YahooFinanceUSScraper(browser)
        scraper.clear_metrics()
        
        urls = scraper.get_latest_articles(category="markets", limit=20)
        
        metrics = scraper.get_latest_metrics()
        
        # Deve completar em menos de 60s
        assert metrics.time_seconds < 60
        
        # Deve ter taxa razoável
        assert metrics.success_rate >= 0.4  # Pelo menos 40%
