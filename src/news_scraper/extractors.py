"""
Múltiplas estratégias de extração de conteúdo com fallbacks automáticos.

Cada extrator implementa uma estratégia diferente para extrair conteúdo de artigos.
O sistema tenta cada estratégia até encontrar uma que funcione.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExtractedContent:
    """Resultado da extração de conteúdo."""
    title: Optional[str] = None
    text: Optional[str] = None
    authors: list[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    language: Optional[str] = None
    tags: list[str] = None
    source: Optional[str] = None
    
    # Metadados da extração
    extractor: Optional[str] = None  # Nome do extrator usado
    confidence: float = 0.0  # 0.0 a 1.0
    html_length: int = 0
    text_length: int = 0
    
    def __post_init__(self):
        if self.authors is None:
            self.authors = []
        if self.tags is None:
            self.tags = []
    
    def is_valid(self, min_text_length: int = 100) -> bool:
        """Verifica se a extração é válida."""
        return (
            self.title is not None
            and len(self.title.strip()) > 0
            and self.text is not None
            and len(self.text.strip()) >= min_text_length
        )
    
    def quality_score(self) -> float:
        """Calcula score de qualidade (0.0 a 1.0)."""
        score = 0.0
        
        # Title (30%)
        if self.title and len(self.title.strip()) > 10:
            score += 0.3
        
        # Text (40%)
        if self.text:
            text_len = len(self.text.strip())
            if text_len >= 500:
                score += 0.4
            elif text_len >= 100:
                score += 0.2
        
        # Date (10%)
        if self.date:
            score += 0.1
        
        # Authors (10%)
        if self.authors and len(self.authors) > 0:
            score += 0.1
        
        # Description (5%)
        if self.description:
            score += 0.05
        
        # Image (5%)
        if self.image:
            score += 0.05
        
        return min(score, 1.0)


class ContentExtractor(ABC):
    """Interface base para extratores de conteúdo."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do extrator."""
        pass
    
    @abstractmethod
    def extract(self, html: str, url: str) -> Optional[ExtractedContent]:
        """
        Extrai conteúdo do HTML.
        
        Args:
            html: HTML da página
            url: URL da página
            
        Returns:
            ExtractedContent ou None se falhar
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o extrator está disponível (dependências instaladas)."""
        pass


class Newspaper3kExtractor(ContentExtractor):
    """Extrator usando newspaper3k."""
    
    @property
    def name(self) -> str:
        return "newspaper3k"
    
    def is_available(self) -> bool:
        try:
            import newspaper
            return True
        except ImportError:
            return False
    
    def extract(self, html: str, url: str) -> Optional[ExtractedContent]:
        try:
            from newspaper import Article
            
            article = Article(url)
            article.set_html(html)
            article.parse()
            
            # Tentar extrair metadados adicionais
            try:
                article.nlp()
            except:
                pass
            
            return ExtractedContent(
                title=article.title,
                text=article.text,
                authors=list(article.authors) if article.authors else [],
                date=article.publish_date.isoformat() if article.publish_date else None,
                description=article.meta_description,
                image=article.top_image,
                language=article.meta_lang,
                tags=list(article.keywords) if hasattr(article, 'keywords') else [],
                extractor=self.name,
                html_length=len(html),
                text_length=len(article.text) if article.text else 0,
            )
        except Exception as e:
            logger.debug(f"Newspaper3k extraction failed: {e}")
            return None


class TrafilaturaExtractor(ContentExtractor):
    """Extrator usando trafilatura (mais robusto)."""
    
    @property
    def name(self) -> str:
        return "trafilatura"
    
    def is_available(self) -> bool:
        try:
            import trafilatura
            return True
        except ImportError:
            return False
    
    def extract(self, html: str, url: str) -> Optional[ExtractedContent]:
        try:
            import trafilatura
            from trafilatura import extract_metadata
            
            # Extrair conteúdo
            text = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
            )
            
            if not text:
                return None
            
            # Extrair metadados
            metadata = extract_metadata(html)
            
            return ExtractedContent(
                title=metadata.title if metadata else None,
                text=text,
                authors=[metadata.author] if metadata and metadata.author else [],
                date=metadata.date if metadata else None,
                description=metadata.description if metadata else None,
                image=metadata.image if metadata else None,
                language=metadata.language if metadata else None,
                tags=metadata.tags if metadata and metadata.tags else [],
                extractor=self.name,
                html_length=len(html),
                text_length=len(text),
            )
        except Exception as e:
            logger.debug(f"Trafilatura extraction failed: {e}")
            return None


class BeautifulSoupExtractor(ContentExtractor):
    """Extrator usando BeautifulSoup com heurísticas."""
    
    @property
    def name(self) -> str:
        return "beautifulsoup"
    
    def is_available(self) -> bool:
        try:
            from bs4 import BeautifulSoup
            return True
        except ImportError:
            return False
    
    def extract(self, html: str, url: str) -> Optional[ExtractedContent]:
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Título - múltiplas estratégias
            title = None
            for selector in ['h1', 'meta[property="og:title"]', 'meta[name="twitter:title"]', 'title']:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get('content') if elem.name == 'meta' else elem.get_text(strip=True)
                    if title:
                        break
            
            # Texto - procurar por tags comuns de artigo
            text_parts = []
            for selector in ['article', 'main', '.article-content', '.post-content', '.entry-content']:
                elem = soup.select_one(selector)
                if elem:
                    # Remover scripts e styles
                    for tag in elem(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                        tag.decompose()
                    
                    # Extrair parágrafos
                    paragraphs = elem.find_all('p')
                    text_parts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20]
                    if text_parts:
                        break
            
            text = '\n\n'.join(text_parts) if text_parts else None
            
            # Metadados
            description = None
            for selector in ['meta[property="og:description"]', 'meta[name="description"]']:
                elem = soup.select_one(selector)
                if elem:
                    description = elem.get('content')
                    if description:
                        break
            
            image = None
            for selector in ['meta[property="og:image"]', 'meta[name="twitter:image"]']:
                elem = soup.select_one(selector)
                if elem:
                    image = elem.get('content')
                    if image:
                        break
            
            # Data
            date = None
            for selector in ['meta[property="article:published_time"]', 'time[datetime]']:
                elem = soup.select_one(selector)
                if elem:
                    date = elem.get('content') or elem.get('datetime')
                    if date:
                        break
            
            # Autores
            authors = []
            for selector in ['meta[property="article:author"]', 'meta[name="author"]', '.author']:
                elems = soup.select(selector)
                for elem in elems:
                    author = elem.get('content') if elem.name == 'meta' else elem.get_text(strip=True)
                    if author and author not in authors:
                        authors.append(author)
            
            if not text or not title:
                return None
            
            return ExtractedContent(
                title=title,
                text=text,
                authors=authors,
                date=date,
                description=description,
                image=image,
                extractor=self.name,
                html_length=len(html),
                text_length=len(text) if text else 0,
            )
        except Exception as e:
            logger.debug(f"BeautifulSoup extraction failed: {e}")
            return None


class ReadabilityExtractor(ContentExtractor):
    """Extrator usando readability (python-readability)."""
    
    @property
    def name(self) -> str:
        return "readability"
    
    def is_available(self) -> bool:
        try:
            from readability import Document
            return True
        except ImportError:
            return False
    
    def extract(self, html: str, url: str) -> Optional[ExtractedContent]:
        try:
            from readability import Document
            from bs4 import BeautifulSoup
            
            doc = Document(html)
            
            title = doc.title()
            summary_html = doc.summary()
            
            # Extrair texto do summary
            soup = BeautifulSoup(summary_html, 'html.parser')
            paragraphs = soup.find_all('p')
            text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
            
            if not text or not title:
                return None
            
            return ExtractedContent(
                title=title,
                text=text,
                extractor=self.name,
                html_length=len(html),
                text_length=len(text),
            )
        except Exception as e:
            logger.debug(f"Readability extraction failed: {e}")
            return None


class CustomSelectorExtractor(ContentExtractor):
    """Extrator usando seletores CSS customizados por domínio."""
    
    def __init__(self, selectors: dict[str, dict]):
        """
        Args:
            selectors: Dicionário com seletores por domínio
                {
                    "infomoney.com.br": {
                        "title": "h1.article-title",
                        "text": "div.article-body p",
                        "date": "time.published",
                        "author": "span.author-name"
                    }
                }
        """
        self.selectors = selectors
    
    @property
    def name(self) -> str:
        return "custom_selector"
    
    def is_available(self) -> bool:
        try:
            from bs4 import BeautifulSoup
            return True
        except ImportError:
            return False
    
    def extract(self, html: str, url: str) -> Optional[ExtractedContent]:
        try:
            from bs4 import BeautifulSoup
            from urllib.parse import urlparse
            
            domain = urlparse(url).netloc
            
            # Procurar seletores para este domínio
            domain_selectors = None
            for key in self.selectors:
                if key in domain:
                    domain_selectors = self.selectors[key]
                    break
            
            if not domain_selectors:
                return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extrair usando seletores customizados
            title = None
            if 'title' in domain_selectors:
                elem = soup.select_one(domain_selectors['title'])
                if elem:
                    title = elem.get_text(strip=True)
            
            text_parts = []
            if 'text' in domain_selectors:
                elems = soup.select(domain_selectors['text'])
                text_parts = [e.get_text(strip=True) for e in elems if len(e.get_text(strip=True)) > 20]
            
            text = '\n\n'.join(text_parts) if text_parts else None
            
            date = None
            if 'date' in domain_selectors:
                elem = soup.select_one(domain_selectors['date'])
                if elem:
                    date = elem.get('datetime') or elem.get_text(strip=True)
            
            authors = []
            if 'author' in domain_selectors:
                elems = soup.select(domain_selectors['author'])
                authors = [e.get_text(strip=True) for e in elems]
            
            if not text or not title:
                return None
            
            return ExtractedContent(
                title=title,
                text=text,
                authors=authors,
                date=date,
                source=domain,
                extractor=self.name,
                html_length=len(html),
                text_length=len(text),
            )
        except Exception as e:
            logger.debug(f"Custom selector extraction failed: {e}")
            return None


class ExtractionPipeline:
    """Pipeline de extração com múltiplos métodos e fallback automático."""
    
    def __init__(self, extractors: list[ContentExtractor] = None):
        """
        Args:
            extractors: Lista de extratores a usar (na ordem de prioridade)
        """
        if extractors is None:
            # Ordem padrão: do mais específico ao mais genérico
            extractors = [
                CustomSelectorExtractor(self._default_selectors()),
                TrafilaturaExtractor(),
                Newspaper3kExtractor(),
                ReadabilityExtractor(),
                BeautifulSoupExtractor(),
            ]
        
        # Filtrar apenas extratores disponíveis
        self.extractors = [e for e in extractors if e.is_available()]
        
        if not self.extractors:
            logger.warning("No extractors available! Install dependencies.")
    
    def _default_selectors(self) -> dict:
        """Seletores padrão para sites conhecidos."""
        return {
            "infomoney.com.br": {
                "title": "h1.article-title, h1.entry-title",
                "text": "div.article-body p, div.entry-content p",
                "date": "time.published, meta[property='article:published_time']",
                "author": "span.author-name, a.author-link",
            },
            "moneytimes.com.br": {
                "title": "h1.post-title",
                "text": "div.post-content p",
                "date": "time.entry-date",
                "author": "span.author",
            },
            "valor.globo.com": {
                "title": "h1.content-head__title",
                "text": "article.content p",
                "date": "time",
            },
            "bloomberg.com": {
                "title": "h1.article-headline",
                "text": "article p",
                "date": "time",
            },
            "einvestidor.estadao.com.br": {
                "title": "h1.article-title",
                "text": "article p",
                "date": "time",
            },
        }
    
    def extract(self, html: str, url: str, min_quality: float = 0.3) -> Optional[ExtractedContent]:
        """
        Extrai conteúdo tentando múltiplos métodos.
        
        Args:
            html: HTML da página
            url: URL da página
            min_quality: Score mínimo de qualidade (0.0 a 1.0)
            
        Returns:
            ExtractedContent com melhor qualidade ou None
        """
        best_result = None
        best_score = 0.0
        
        for extractor in self.extractors:
            try:
                logger.debug(f"Trying extractor: {extractor.name}")
                result = extractor.extract(html, url)
                
                if result and result.is_valid():
                    score = result.quality_score()
                    result.confidence = score
                    
                    logger.debug(f"{extractor.name} quality score: {score:.2f}")
                    
                    if score > best_score:
                        best_score = score
                        best_result = result
                    
                    # Se conseguiu score alto, não precisa tentar outros
                    if score >= 0.8:
                        logger.info(f"High quality extraction with {extractor.name}: {score:.2f}")
                        break
            except Exception as e:
                logger.debug(f"Extractor {extractor.name} failed: {e}")
                continue
        
        if best_result and best_score >= min_quality:
            logger.info(f"Best extraction: {best_result.extractor} (score: {best_score:.2f})")
            return best_result
        
        logger.warning(f"No extraction met quality threshold {min_quality}")
        return None
    
    def extract_all(self, html: str, url: str) -> list[ExtractedContent]:
        """
        Tenta todos os extratores e retorna todos os resultados válidos.
        Útil para comparação e debugging.
        """
        results = []
        
        for extractor in self.extractors:
            try:
                result = extractor.extract(html, url)
                if result and result.is_valid():
                    result.confidence = result.quality_score()
                    results.append(result)
            except Exception as e:
                logger.debug(f"Extractor {extractor.name} failed: {e}")
                continue
        
        # Ordenar por qualidade
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results
