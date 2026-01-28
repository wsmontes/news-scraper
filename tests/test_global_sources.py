"""
Testes para os scrapers de fontes globais.
"""

import pytest
from news_scraper.global_sources import GlobalNewsManager


class TestGlobalNewsManager:
    """Testa gerenciador de fontes globais."""
    
    def test_total_sources(self):
        """Verifica número total de fontes."""
        assert len(GlobalNewsManager.SOURCES) >= 19
    
    def test_get_source_info(self):
        """Testa obtenção de informações da fonte."""
        info = GlobalNewsManager.get_source_info("bloomberg")
        assert info is not None
        assert info["name"] == "Bloomberg"
        assert info["country"] == "US"
        assert info["language"] == "en"
    
    def test_list_sources_by_country(self):
        """Testa filtro por país."""
        us_sources = GlobalNewsManager.list_sources(country="US")
        assert len(us_sources) >= 11
        assert "bloomberg" in us_sources
        assert "cnbc" in us_sources
        assert "yahoofinance" in us_sources
        assert "businessinsider" in us_sources
        assert "investing" in us_sources
        
        br_sources = GlobalNewsManager.list_sources(country="BR")
        assert len(br_sources) >= 4
        assert "infomoney" in br_sources
        assert "moneytimes" in br_sources
    
    def test_list_sources_by_language(self):
        """Testa filtro por idioma."""
        en_sources = GlobalNewsManager.list_sources(language="en")
        assert len(en_sources) >= 15
        
        pt_sources = GlobalNewsManager.list_sources(language="pt")
        assert len(pt_sources) >= 4
    
    def test_list_free_sources(self):
        """Testa filtro de fontes sem paywall."""
        free_sources = GlobalNewsManager.list_sources(no_paywall=True)
        assert len(free_sources) >= 13
        assert "bloomberg" in free_sources
        assert "reuters" in free_sources
        assert "yahoofinance" in free_sources
        assert "investing" in free_sources
        assert "bloomberg-latam" in free_sources
        # Deve incluir parciais (são considerados "free" com limitações)
        assert "businessinsider" in free_sources
        assert "seekingalpha" in free_sources
        # Não deve incluir paywalls completos
        assert "ft" not in free_sources
        assert "wsj" not in free_sources
        assert "valor" not in free_sources
    
    def test_get_global_sources(self):
        """Testa obtenção de fontes globais."""
        global_sources = GlobalNewsManager.get_global_sources()
        assert len(global_sources) >= 15
        assert all(GlobalNewsManager.get_source_info(s)["language"] == "en" for s in global_sources)
    
    def test_get_brazilian_sources(self):
        """Testa obtenção de fontes brasileiras."""
        br_sources = GlobalNewsManager.get_brazilian_sources()
        assert len(br_sources) >= 4
        assert all(GlobalNewsManager.get_source_info(s)["country"] == "BR" for s in br_sources)
    
    def test_all_sources_have_required_fields(self):
        """Verifica que todas as fontes têm campos obrigatórios."""
        required_fields = ["name", "country", "language", "paywall", "categories", "module", "class"]
        
        for source_id, info in GlobalNewsManager.SOURCES.items():
            for field in required_fields:
                assert field in info, f"Source {source_id} missing field: {field}"
            
            assert len(info["categories"]) > 0, f"Source {source_id} has no categories"
    
    def test_unknown_source(self):
        """Testa fonte inexistente."""
        info = GlobalNewsManager.get_source_info("fonte_invalida")
        assert info is None
    
    def test_source_categories(self):
        """Verifica categorias das fontes."""
        # Bloomberg
        bloomberg = GlobalNewsManager.get_source_info("bloomberg")
        assert "markets" in bloomberg["categories"]
        
        # InfoMoney
        infomoney = GlobalNewsManager.get_source_info("infomoney")
        assert "mercados" in infomoney["categories"]
        
        # Reuters
        reuters = GlobalNewsManager.get_source_info("reuters")
        assert "business" in reuters["categories"]
        
        # Yahoo Finance US (nova fonte)
        yahoo = GlobalNewsManager.get_source_info("yahoofinance")
        assert "stock-market-news" in yahoo["categories"]
        assert "latest-news" in yahoo["categories"]
        
        # Business Insider (nova fonte)
        bi = GlobalNewsManager.get_source_info("businessinsider")
        assert "markets" in bi["categories"]
        assert bi["paywall"] == "partial"
        
        # Investing.com (nova fonte)
        investing = GlobalNewsManager.get_source_info("investing")
        assert "news" in investing["categories"]
        assert "stock-market-news" in investing["categories"]
        
        # Bloomberg Latin America (nova fonte)
        bloomberg_latam = GlobalNewsManager.get_source_info("bloomberg-latam")
        assert "latinamerica" in bloomberg_latam["categories"]
        assert bloomberg_latam["paywall"] == False


class TestSourcesMetadata:
    """Testa metadados das fontes."""
    
    @pytest.mark.parametrize("source_id", [
        "bloomberg", "ft", "wsj", "reuters", "cnbc", "marketwatch",
        "seekingalpha", "economist", "forbes", "barrons", "investopedia",
        "yahoofinance", "businessinsider", "investing", "bloomberg-latam",
        "infomoney", "moneytimes", "valor", "einvestidor"
    ])
    def test_source_exists(self, source_id):
        """Verifica que todas as fontes principais existem."""
        info = GlobalNewsManager.get_source_info(source_id)
        assert info is not None
        assert info["name"] is not None
    
    def test_paywall_types(self):
        """Verifica tipos de paywall válidos."""
        valid_paywalls = [True, False, "partial"]
        
        for source_id, info in GlobalNewsManager.SOURCES.items():
            assert info["paywall"] in valid_paywalls, f"Invalid paywall type for {source_id}"
    
    def test_country_codes(self):
        """Verifica códigos de país válidos."""
        valid_countries = ["US", "UK", "BR"]
        
        for source_id, info in GlobalNewsManager.SOURCES.items():
            assert info["country"] in valid_countries, f"Invalid country for {source_id}"
    
    def test_language_codes(self):
        """Verifica códigos de idioma válidos."""
        valid_languages = ["en", "pt"]
        
        for source_id, info in GlobalNewsManager.SOURCES.items():
            assert info["language"] in valid_languages, f"Invalid language for {source_id}"


def test_sources_distribution():
    """Testa distribuição de fontes."""
    # Agrupar por país
    by_country = {}
    for source_id, info in GlobalNewsManager.SOURCES.items():
        country = info["country"]
        by_country[country] = by_country.get(country, 0) + 1
    
    print(f"\nDistribuição por país: {by_country}")
    
    # US deve ter mais fontes
    assert by_country.get("US", 0) >= 11
    # BR deve ter pelo menos 4
    assert by_country.get("BR", 0) >= 4
    # UK deve ter pelo menos 3
    assert by_country.get("UK", 0) >= 3


def test_scraper_modules_naming():
    """Verifica nomenclatura dos módulos."""
    for source_id, info in GlobalNewsManager.SOURCES.items():
        # Module deve terminar com _scraper
        assert info["module"].endswith("_scraper"), f"Invalid module name for {source_id}"
        
        # Class deve terminar com Scraper
        assert info["class"].endswith("Scraper"), f"Invalid class name for {source_id}"
