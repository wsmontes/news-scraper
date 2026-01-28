"""
Testes para extractors.py - múltiplas estratégias de extração.
"""

import pytest
from news_scraper.extractors import (
    ExtractedContent,
    Newspaper3kExtractor,
    TrafilaturaExtractor,
    BeautifulSoupExtractor,
    ReadabilityExtractor,
    CustomSelectorExtractor,
    ExtractionPipeline,
)


# HTML de teste simples
SIMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Artigo de Teste</title>
    <meta property="og:title" content="Título do Artigo">
    <meta property="og:description" content="Descrição do artigo">
    <meta property="article:published_time" content="2026-01-28T10:00:00">
    <meta name="author" content="João Silva">
</head>
<body>
    <article>
        <h1>Título do Artigo</h1>
        <time datetime="2026-01-28">28 de janeiro de 2026</time>
        <p>Este é o primeiro parágrafo do artigo de teste com conteúdo suficiente para passar na validação de tamanho mínimo.</p>
        <p>Este é o segundo parágrafo com mais conteúdo para garantir que temos texto suficiente para uma extração válida.</p>
        <p>Terceiro parágrafo com ainda mais informação para simular um artigo real de notícias financeiras com dados relevantes.</p>
    </article>
</body>
</html>
"""


class TestExtractedContent:
    """Testa classe ExtractedContent."""
    
    def test_is_valid(self):
        """Testa validação de conteúdo."""
        # Válido
        content = ExtractedContent(
            title="Título Teste",
            text="Texto longo" * 20,
        )
        assert content.is_valid()
        
        # Inválido - sem título
        content = ExtractedContent(text="Texto longo" * 20)
        assert not content.is_valid()
        
        # Inválido - texto muito curto
        content = ExtractedContent(title="Título", text="Curto")
        assert not content.is_valid()
    
    def test_quality_score(self):
        """Testa cálculo de score de qualidade."""
        # Score alto - todos os campos
        content = ExtractedContent(
            title="Título Completo",
            text="Texto longo" * 100,
            date="2026-01-28",
            authors=["Autor 1"],
            description="Descrição",
            image="http://example.com/image.jpg",
        )
        score = content.quality_score()
        assert score >= 0.8
        
        # Score baixo - apenas título e texto curto
        content = ExtractedContent(
            title="Título",
            text="Texto curto",
        )
        score = content.quality_score()
        assert score < 0.5


class TestBeautifulSoupExtractor:
    """Testa extrator BeautifulSoup."""
    
    def test_is_available(self):
        """BeautifulSoup deve estar disponível."""
        extractor = BeautifulSoupExtractor()
        assert extractor.is_available()
    
    def test_extract_simple_html(self):
        """Testa extração de HTML simples."""
        extractor = BeautifulSoupExtractor()
        result = extractor.extract(SIMPLE_HTML, "http://example.com/article")
        
        assert result is not None
        assert result.title is not None
        assert "Artigo" in result.title or "Título" in result.title
        assert result.text is not None
        assert len(result.text) > 100
        assert result.extractor == "beautifulsoup"


class TestTrafilaturaExtractor:
    """Testa extrator Trafilatura."""
    
    def test_is_available(self):
        """Verifica se trafilatura está instalado."""
        extractor = TrafilaturaExtractor()
        # Pode ou não estar instalado
        assert isinstance(extractor.is_available(), bool)
    
    @pytest.mark.skipif(
        not TrafilaturaExtractor().is_available(),
        reason="trafilatura not installed"
    )
    def test_extract_simple_html(self):
        """Testa extração com trafilatura."""
        extractor = TrafilaturaExtractor()
        result = extractor.extract(SIMPLE_HTML, "http://example.com/article")
        
        if result:  # Pode retornar None se não conseguir extrair
            assert result.extractor == "trafilatura"
            assert result.text is not None


class TestCustomSelectorExtractor:
    """Testa extrator com seletores customizados."""
    
    def test_extract_with_custom_selectors(self):
        """Testa extração com seletores específicos."""
        selectors = {
            "example.com": {
                "title": "h1",
                "text": "article p",
                "date": "time",
            }
        }
        
        extractor = CustomSelectorExtractor(selectors)
        result = extractor.extract(SIMPLE_HTML, "http://example.com/article")
        
        assert result is not None
        assert result.title is not None
        assert result.text is not None
        assert result.extractor == "custom_selector"
    
    def test_no_matching_selectors(self):
        """Testa quando não há seletores para o domínio."""
        selectors = {
            "othersite.com": {
                "title": "h1",
                "text": "p",
            }
        }
        
        extractor = CustomSelectorExtractor(selectors)
        result = extractor.extract(SIMPLE_HTML, "http://example.com/article")
        
        # Deve retornar None pois não há seletores para example.com
        assert result is None


class TestExtractionPipeline:
    """Testa pipeline de extração."""
    
    def test_pipeline_creation(self):
        """Testa criação do pipeline."""
        pipeline = ExtractionPipeline()
        assert len(pipeline.extractors) > 0
    
    def test_extract_with_pipeline(self):
        """Testa extração usando pipeline."""
        pipeline = ExtractionPipeline()
        result = pipeline.extract(SIMPLE_HTML, "http://example.com/article")
        
        # Pelo menos um extrator deve funcionar
        assert result is not None
        assert result.is_valid()
        assert result.extractor is not None
        assert result.confidence > 0
    
    def test_extract_all(self):
        """Testa extração com todos os métodos."""
        pipeline = ExtractionPipeline()
        results = pipeline.extract_all(SIMPLE_HTML, "http://example.com/article")
        
        # Deve ter pelo menos 1 resultado
        assert len(results) > 0
        
        # Resultados devem estar ordenados por qualidade
        if len(results) > 1:
            assert results[0].confidence >= results[-1].confidence
    
    def test_min_quality_threshold(self):
        """Testa threshold de qualidade mínima."""
        pipeline = ExtractionPipeline()
        
        # HTML muito ruim
        bad_html = "<html><body><p>x</p></body></html>"
        result = pipeline.extract(bad_html, "http://example.com", min_quality=0.5)
        
        # Deve retornar None se não atingir qualidade mínima
        # (ou retornar algo com qualidade >= 0.5)
        if result:
            assert result.quality_score() >= 0.5


class TestExtractionWithRealSite:
    """Testes com HTML mais realista."""
    
    def test_infomoney_style_html(self):
        """Testa HTML no estilo InfoMoney."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fed mantém taxa de juros em 5,5% | InfoMoney</title>
            <meta property="og:title" content="Fed mantém taxa de juros em 5,5%">
            <meta property="article:published_time" content="2026-01-28T14:30:00">
        </head>
        <body>
            <article class="article-body">
                <h1 class="article-title">Fed mantém taxa de juros em 5,5%</h1>
                <time class="published">28/01/2026</time>
                <div class="entry-content">
                    <p>O Federal Reserve dos Estados Unidos decidiu manter a taxa de juros em 5,5% ao ano nesta quarta-feira.</p>
                    <p>A decisão foi unânime entre os membros do comitê e reflete a cautela da autoridade monetária com a inflação persistente.</p>
                    <p>O presidente do Fed, Jerome Powell, afirmou em entrevista coletiva que o banco central continuará monitorando os dados econômicos.</p>
                </div>
            </article>
        </body>
        </html>
        """
        
        # Configurar pipeline com seletores InfoMoney
        selectors = {
            "example.com": {
                "title": "h1.article-title",
                "text": "div.entry-content p",
                "date": "time.published",
            }
        }
        
        custom_extractor = CustomSelectorExtractor(selectors)
        pipeline = ExtractionPipeline([custom_extractor, BeautifulSoupExtractor()])
        
        result = pipeline.extract(html, "http://example.com/article")
        
        assert result is not None
        assert "Fed" in result.title
        assert "Federal Reserve" in result.text
        assert len(result.text) > 100


def test_extraction_fallback_order():
    """Testa ordem de fallback dos extratores."""
    pipeline = ExtractionPipeline()
    
    # Verificar que há múltiplos extratores
    assert len(pipeline.extractors) >= 2
    
    # Primeira tentativa deve ser custom (se disponível) ou trafilatura
    first_extractor = pipeline.extractors[0]
    assert first_extractor.name in ["custom_selector", "trafilatura", "newspaper3k"]
