"""
Ferramentas profissionais para scraping de alto nível.

Inclui:
- Detecção de paywall
- Limpeza de texto avançada
- Validação de conteúdo
- Normalização de datas
- Detecção de idioma
- User agent management
- Rate limiting
- Retry strategies
- Cache
- Anti-bot detection evasion
"""

from __future__ import annotations

import time
import hashlib
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# USER AGENT MANAGEMENT
# ============================================================================

class UserAgentRotator:
    """Rotaciona user agents para evitar detecção."""
    
    # User agents realistas e modernos
    USER_AGENTS = [
        # Chrome no Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        
        # Chrome no Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        
        # Firefox no Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        
        # Firefox no Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        
        # Safari no Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        
        # Edge no Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]
    
    def __init__(self):
        self._index = 0
    
    def get_random(self) -> str:
        """Retorna user agent aleatório."""
        import random
        return random.choice(self.USER_AGENTS)
    
    def get_next(self) -> str:
        """Retorna próximo user agent (round-robin)."""
        ua = self.USER_AGENTS[self._index]
        self._index = (self._index + 1) % len(self.USER_AGENTS)
        return ua
    
    def get_browser_headers(self, url: str = None) -> dict[str, str]:
        """Retorna headers completos que simulam navegador real."""
        return {
            "User-Agent": self.get_random(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """Rate limiter simples mas efetivo."""
    
    def __init__(self, requests_per_second: float = 1.0):
        """
        Args:
            requests_per_second: Máximo de requisições por segundo
        """
        self.min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self._last_request = {}
    
    def wait_if_needed(self, key: str = "default") -> float:
        """
        Espera se necessário para respeitar rate limit.
        
        Args:
            key: Chave para rate limit independente (ex: domínio)
            
        Returns:
            Tempo esperado em segundos
        """
        now = time.time()
        
        if key in self._last_request:
            elapsed = now - self._last_request[key]
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s for {key}")
                time.sleep(wait_time)
                self._last_request[key] = time.time()
                return wait_time
        
        self._last_request[key] = now
        return 0.0


class DomainRateLimiter:
    """Rate limiter por domínio com configurações customizadas."""
    
    def __init__(self, default_delay: float = 2.0):
        """
        Args:
            default_delay: Delay padrão entre requisições (segundos)
        """
        self.default_delay = default_delay
        self._domain_delays = {}
        self._last_request = {}
    
    def set_domain_delay(self, domain: str, delay: float):
        """Define delay específico para um domínio."""
        self._domain_delays[domain] = delay
    
    def wait(self, domain: str):
        """Espera o tempo necessário antes de fazer requisição."""
        delay = self._domain_delays.get(domain, self.default_delay)
        
        if domain in self._last_request:
            elapsed = time.time() - self._last_request[domain]
            if elapsed < delay:
                wait_time = delay - elapsed
                logger.debug(f"Waiting {wait_time:.2f}s for {domain}")
                time.sleep(wait_time)
        
        self._last_request[domain] = time.time()


# ============================================================================
# RETRY STRATEGIES
# ============================================================================

@dataclass
class RetryConfig:
    """Configuração de retry."""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


class RetryStrategy:
    """Estratégia de retry com backoff exponencial."""
    
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
    
    def execute(self, func, *args, **kwargs):
        """
        Executa função com retry automático.
        
        Raises:
            Exception: Se todas as tentativas falharem
        """
        import random
        
        last_exception = None
        delay = self.config.initial_delay
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.config.max_attempts:
                    logger.error(f"All {self.config.max_attempts} attempts failed")
                    raise
                
                # Calcular delay com backoff exponencial
                if self.config.jitter:
                    jitter_factor = random.uniform(0.5, 1.5)
                    actual_delay = min(delay * jitter_factor, self.config.max_delay)
                else:
                    actual_delay = min(delay, self.config.max_delay)
                
                logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {actual_delay:.2f}s...")
                time.sleep(actual_delay)
                
                delay *= self.config.exponential_base
        
        raise last_exception


# ============================================================================
# CACHE
# ============================================================================

class SimpleCache:
    """Cache simples em disco para respostas HTTP."""
    
    def __init__(self, cache_dir: Path, ttl_hours: int = 24):
        """
        Args:
            cache_dir: Diretório para cache
            ttl_hours: Tempo de vida do cache em horas
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_path(self, key: str) -> Path:
        """Retorna caminho do arquivo de cache."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """Retorna valor do cache se válido."""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            data = json.loads(cache_path.read_text())
            cached_at = datetime.fromisoformat(data['cached_at'])
            
            # Verificar se expirou
            if datetime.now() - cached_at > self.ttl:
                logger.debug(f"Cache expired for {key}")
                cache_path.unlink()
                return None
            
            logger.debug(f"Cache hit for {key}")
            return data['value']
        except Exception as e:
            logger.debug(f"Cache read error: {e}")
            return None
    
    def set(self, key: str, value: Any):
        """Salva valor no cache."""
        cache_path = self._get_cache_path(key)
        
        try:
            data = {
                'cached_at': datetime.now().isoformat(),
                'value': value,
            }
            cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
            logger.debug(f"Cached {key}")
        except Exception as e:
            logger.debug(f"Cache write error: {e}")
    
    def clear_expired(self):
        """Remove entradas expiradas do cache."""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                data = json.loads(cache_file.read_text())
                cached_at = datetime.fromisoformat(data['cached_at'])
                
                if datetime.now() - cached_at > self.ttl:
                    cache_file.unlink()
                    count += 1
            except Exception:
                # Arquivo corrompido, remover
                cache_file.unlink()
                count += 1
        
        if count > 0:
            logger.info(f"Cleared {count} expired cache entries")


# ============================================================================
# PAYWALL DETECTION
# ============================================================================

class PaywallDetector:
    """Detecta paywalls e conteúdo bloqueado."""
    
    # Padrões comuns de paywall
    PAYWALL_INDICATORS = [
        # Português
        "assine", "assinante", "conteúdo exclusivo", "área exclusiva",
        "acesso restrito", "continue lendo", "libere este conteúdo",
        "faça login", "cadastre-se grátis", "premium",
        
        # Inglês
        "subscribe", "subscriber", "exclusive content", "restricted access",
        "sign in", "register", "premium", "membership required",
        "paywall", "paid content",
    ]
    
    # Seletores CSS comuns de paywall
    PAYWALL_SELECTORS = [
        ".paywall", "#paywall", ".subscription-required",
        ".login-required", ".premium-content", ".subscriber-only",
        '[data-paywall]', '.article-lock', '.content-gate',
    ]
    
    def detect(self, html: str, text: str = None) -> dict:
        """
        Detecta presença de paywall.
        
        Returns:
            Dict com: has_paywall (bool), confidence (float), indicators (list)
        """
        indicators = []
        
        # Verificar texto
        html_lower = html.lower()
        for indicator in self.PAYWALL_INDICATORS:
            if indicator.lower() in html_lower:
                indicators.append(f"text:{indicator}")
        
        # Verificar seletores CSS
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            for selector in self.PAYWALL_SELECTORS:
                if soup.select_one(selector):
                    indicators.append(f"selector:{selector}")
        except:
            pass
        
        # Verificar tamanho do texto (paywall geralmente tem pouco conteúdo)
        if text and len(text.strip()) < 200:
            indicators.append("short_text")
        
        confidence = min(len(indicators) * 0.3, 1.0)
        
        return {
            "has_paywall": len(indicators) > 0,
            "confidence": confidence,
            "indicators": indicators,
        }


# ============================================================================
# TEXT CLEANING
# ============================================================================

class TextCleaner:
    """Limpeza avançada de texto extraído."""
    
    @staticmethod
    def clean(text: str) -> str:
        """Limpa texto removendo artefatos comuns."""
        if not text:
            return ""
        
        # Remover múltiplas quebras de linha
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remover espaços múltiplos
        text = re.sub(r' {2,}', ' ', text)
        
        # Remover tabs
        text = text.replace('\t', ' ')
        
        # Remover espaços no início/fim de cada linha
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remover linhas muito curtas (geralmente lixo)
        lines = [line for line in text.split('\n') if len(line.strip()) > 3 or line.strip() == '']
        text = '\n'.join(lines)
        
        return text.strip()
    
    @staticmethod
    def remove_boilerplate(text: str) -> str:
        """Remove textos padrão (copyright, rodapé, etc)."""
        # Padrões comuns de boilerplate
        boilerplate_patterns = [
            r'todos os direitos reservados.*',
            r'© \d{4}.*',
            r'copyright.*',
            r'compartilhe:?\s*(facebook|twitter|whatsapp|linkedin).*',
            r'siga-nos.*',
            r'assine nossa newsletter.*',
            r'receba notícias.*',
        ]
        
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return TextCleaner.clean(text)
    
    @staticmethod
    def extract_paragraphs(text: str, min_length: int = 50) -> list[str]:
        """Extrai parágrafos válidos (acima do tamanho mínimo)."""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if len(p.strip()) >= min_length]


# ============================================================================
# DATE NORMALIZATION
# ============================================================================

class DateNormalizer:
    """Normaliza datas em diversos formatos para ISO."""
    
    # Mapeamento de meses em português
    MONTH_MAP_PT = {
        'janeiro': 1, 'jan': 1,
        'fevereiro': 2, 'fev': 2,
        'março': 3, 'mar': 3,
        'abril': 4, 'abr': 4,
        'maio': 5, 'mai': 5,
        'junho': 6, 'jun': 6,
        'julho': 7, 'jul': 7,
        'agosto': 8, 'ago': 8,
        'setembro': 9, 'set': 9,
        'outubro': 10, 'out': 10,
        'novembro': 11, 'nov': 11,
        'dezembro': 12, 'dez': 12,
    }
    
    @classmethod
    def normalize(cls, date_str: str) -> Optional[str]:
        """
        Normaliza data para formato ISO (YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS).
        
        Suporta múltiplos formatos.
        """
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # Já está em formato ISO
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str
        
        # Tentar diversos formatos
        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y',
            '%d/%m/%Y %H:%M',
            '%Y/%m/%d',
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Tentar formato com mês por extenso em português
        # Ex: "28 de janeiro de 2026"
        match = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', date_str, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            month_name = match.group(2).lower()
            year = int(match.group(3))
            
            month = cls.MONTH_MAP_PT.get(month_name)
            if month:
                return f"{year:04d}-{month:02d}-{day:02d}"
        
        logger.debug(f"Could not normalize date: {date_str}")
        return None


# ============================================================================
# CONTENT VALIDATION
# ============================================================================

class ContentValidator:
    """Valida qualidade e integridade do conteúdo extraído."""
    
    @staticmethod
    def validate_title(title: str) -> bool:
        """Valida se título é válido."""
        if not title or len(title.strip()) < 10:
            return False
        
        # Título não deve ser muito longo (provavelmente erro)
        if len(title) > 500:
            return False
        
        # Título não deve ser apenas números ou símbolos
        if not any(c.isalpha() for c in title):
            return False
        
        return True
    
    @staticmethod
    def validate_text(text: str, min_length: int = 100) -> bool:
        """Valida se texto é válido."""
        if not text or len(text.strip()) < min_length:
            return False
        
        # Verificar se tem parágrafos
        paragraphs = [p for p in text.split('\n\n') if len(p.strip()) > 50]
        if len(paragraphs) < 2:
            return False
        
        # Verificar densidade de palavras (não deve ser só código/lixo)
        words = text.split()
        if len(words) < 50:
            return False
        
        return True
    
    @staticmethod
    def is_article_content(text: str) -> bool:
        """Verifica se parece ser conteúdo de artigo (não erro/navegação)."""
        # Verificar tamanho
        if len(text.strip()) < 200:
            return False
        
        # Verificar se tem pontuação de frases
        if text.count('.') < 3:
            return False
        
        # Não deve ser lista de links
        lines = text.split('\n')
        link_lines = sum(1 for line in lines if 'http' in line or 'www.' in line)
        if len(lines) > 0 and link_lines / len(lines) > 0.5:
            return False
        
        return True


# ============================================================================
# LANGUAGE DETECTION
# ============================================================================

class LanguageDetector:
    """Detecta idioma do texto."""
    
    @staticmethod
    def detect(text: str) -> Optional[str]:
        """
        Detecta idioma usando langdetect.
        
        Returns:
            Código ISO 639-1 (ex: 'pt', 'en') ou None
        """
        try:
            from langdetect import detect
            return detect(text[:1000])  # Usar apenas início para performance
        except ImportError:
            logger.debug("langdetect not installed, skipping language detection")
            return None
        except Exception as e:
            logger.debug(f"Language detection failed: {e}")
            return None
    
    @staticmethod
    def is_portuguese(text: str) -> bool:
        """Verifica se texto é em português."""
        lang = LanguageDetector.detect(text)
        return lang == 'pt' if lang else False


# ============================================================================
# ANTI-BOT EVASION
# ============================================================================

class AntiBotEvasion:
    """Técnicas para evitar detecção de bot."""
    
    @staticmethod
    def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Espera tempo aleatório."""
        import random
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    @staticmethod
    def get_realistic_headers(referer: str = None) -> dict[str, str]:
        """Retorna headers realistas."""
        ua_rotator = UserAgentRotator()
        headers = ua_rotator.get_browser_headers()
        
        if referer:
            headers['Referer'] = referer
        
        return headers
    
    @staticmethod
    def should_add_cookies(domain: str) -> bool:
        """Determina se deve adicionar cookies."""
        # Sites que geralmente requerem cookies
        cookie_required = [
            'valor.globo.com',
            'bloomberg.com',
            'wsj.com',
            'ft.com',
        ]
        
        return any(d in domain for d in cookie_required)
