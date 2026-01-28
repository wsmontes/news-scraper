"""
Classe base robusta para todos os scrapers com:
- Sistema de retry automático
- Validação de taxa de sucesso
- Coleta de métricas
- Filtros de data
- Detecção de paywall
"""

from __future__ import annotations
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from .tools import RetryStrategy, RetryConfig, PaywallDetector, RateLimiter

logger = logging.getLogger(__name__)


@dataclass
class ScraperMetrics:
    """Métricas de execução do scraper."""
    source_id: str
    category: Optional[str]
    requested: int
    collected: int
    success_rate: float
    time_seconds: float
    timestamp: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    has_paywall_detected: bool = False
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "source_id": self.source_id,
            "category": self.category,
            "requested": self.requested,
            "collected": self.collected,
            "success_rate": self.success_rate,
            "time_seconds": self.time_seconds,
            "timestamp": self.timestamp.isoformat(),
            "errors": self.errors,
            "has_paywall_detected": self.has_paywall_detected,
            "retry_count": self.retry_count,
        }


class ScraperException(Exception):
    """Exceção base para erros de scraping."""
    pass


class InsufficientDataException(ScraperException):
    """Exceção quando não há dados suficientes coletados."""
    pass


class PaywallException(ScraperException):
    """Exceção quando paywall impede coleta."""
    pass


class BaseScraper(ABC):
    """
    Classe base robusta para todos os scrapers.
    
    Features:
    - Retry automático com exponential backoff
    - Validação de taxa de sucesso mínima
    - Coleta e armazenamento de métricas
    - Filtros de data
    - Detecção de paywall
    - Rate limiting
    """
    
    # Configurações padrão (podem ser sobrescritas por subclasses)
    MIN_SUCCESS_RATE = 0.5  # 50% mínimo
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0
    RATE_LIMIT_DELAY = 1.0
    HAS_PAYWALL = False
    
    def __init__(self, browser_scraper, source_id: str):
        """
        Inicializa scraper base.
        
        Args:
            browser_scraper: Instância do BrowserScraper
            source_id: ID único da fonte
        """
        self.scraper = browser_scraper
        self.source_id = source_id
        self.metrics_history: List[ScraperMetrics] = []
        
        # Inicializar ferramentas
        retry_config = RetryConfig(
            max_attempts=self.MAX_RETRIES,
            initial_delay=self.RETRY_DELAY,
            exponential_base=2.0
        )
        self.retry_strategy = RetryStrategy(config=retry_config)
        self.paywall_detector = PaywallDetector()
        self.rate_limiter = RateLimiter(requests_per_second=0.5)  # 30 requests/minute = 0.5/sec
    
    @abstractmethod
    def _collect_urls(
        self, 
        category: Optional[str] = None, 
        limit: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[str]:
        """
        Método abstrato para coletar URLs.
        Deve ser implementado por cada scraper específico.
        
        Args:
            category: Categoria específica
            limit: Número máximo de URLs
            start_date: Data inicial (filtro)
            end_date: Data final (filtro)
            
        Returns:
            Lista de URLs coletadas
        """
        pass
    
    def get_latest_articles(
        self,
        category: Optional[str] = None,
        limit: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_success_rate: Optional[float] = None,
        raise_on_insufficient: bool = False
    ) -> List[str]:
        """
        Coleta URLs com retry, validação e métricas.
        
        Args:
            category: Categoria específica
            limit: Número máximo de URLs
            start_date: Data inicial (filtro)
            end_date: Data final (filtro)
            min_success_rate: Taxa mínima de sucesso (sobrescreve padrão)
            raise_on_insufficient: Se True, lança exceção quando insuficiente
            
        Returns:
            Lista de URLs coletadas
            
        Raises:
            InsufficientDataException: Se taxa de sucesso < mínimo e raise_on_insufficient=True
            PaywallException: Se paywall detectado e impede coleta
        """
        min_rate = min_success_rate or self.MIN_SUCCESS_RATE
        start_time = time.time()
        errors = []
        retry_count = 0
        urls = []
        
        # Rate limiting
        self.rate_limiter.wait_if_needed(self.source_id)
        
        # Tentar com retry
        for attempt in range(self.MAX_RETRIES):
            try:
                urls = self._collect_urls(
                    category=category,
                    limit=limit,
                    start_date=start_date,
                    end_date=end_date
                )
                
                # Sucesso, sair do loop
                if len(urls) > 0:
                    break
                    
            except Exception as e:
                retry_count = attempt + 1
                error_msg = f"Attempt {attempt + 1} failed: {str(e)}"
                errors.append(error_msg)
                logger.warning(f"[{self.source_id}] {error_msg}")
                
                # Se não é última tentativa, aguardar
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.retry_strategy.get_delay(attempt)
                    logger.info(f"[{self.source_id}] Retrying in {delay:.1f}s...")
                    time.sleep(delay)
        
        elapsed = time.time() - start_time
        
        # Calcular taxa de sucesso
        success_rate = len(urls) / limit if limit > 0 else 0
        
        # Criar métricas
        metrics = ScraperMetrics(
            source_id=self.source_id,
            category=category,
            requested=limit,
            collected=len(urls),
            success_rate=success_rate,
            time_seconds=round(elapsed, 2),
            errors=errors,
            has_paywall_detected=self.HAS_PAYWALL,
            retry_count=retry_count
        )
        
        # Armazenar métricas
        self.metrics_history.append(metrics)
        
        # Validar taxa de sucesso
        if success_rate < min_rate:
            msg = (
                f"[{self.source_id}] Taxa de sucesso baixa: {success_rate:.1%} "
                f"(mínimo: {min_rate:.1%}) - Coletou {len(urls)}/{limit} URLs"
            )
            
            if self.HAS_PAYWALL:
                msg += " [PAYWALL DETECTADO]"
            
            if raise_on_insufficient:
                if self.HAS_PAYWALL:
                    raise PaywallException(msg)
                else:
                    raise InsufficientDataException(msg)
            else:
                logger.warning(msg)
        
        # Log de sucesso
        logger.info(
            f"[{self.source_id}] Coletou {len(urls)}/{limit} URLs "
            f"({success_rate:.1%}) em {elapsed:.2f}s"
        )
        
        return urls
    
    def filter_by_date(
        self,
        urls: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[str]:
        """
        Filtra URLs por data (a ser implementado por scrapers específicos).
        Base implementa sem filtro.
        
        Args:
            urls: Lista de URLs
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            URLs filtradas
        """
        # Implementação base: sem filtro
        # Scrapers específicos devem sobrescrever se suportarem
        if start_date or end_date:
            logger.warning(
                f"[{self.source_id}] Filtro de data não implementado, "
                "retornando todas as URLs"
            )
        return urls
    
    def get_metrics(self) -> List[ScraperMetrics]:
        """Retorna histórico de métricas."""
        return self.metrics_history
    
    def get_latest_metrics(self) -> Optional[ScraperMetrics]:
        """Retorna métricas da última execução."""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_average_success_rate(self) -> float:
        """Calcula taxa de sucesso média."""
        if not self.metrics_history:
            return 0.0
        return sum(m.success_rate for m in self.metrics_history) / len(self.metrics_history)
    
    def clear_metrics(self):
        """Limpa histórico de métricas."""
        self.metrics_history.clear()
    
    def export_metrics(self) -> List[Dict[str, Any]]:
        """Exporta métricas para formato serializável."""
        return [m.to_dict() for m in self.metrics_history]


class MetricsCollector:
    """Coletor central de métricas de todos os scrapers."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.metrics = []
        return cls._instance
    
    def add_metrics(self, metrics: ScraperMetrics):
        """Adiciona métricas ao coletor."""
        self.metrics.append(metrics)
    
    def get_metrics_by_source(self, source_id: str) -> List[ScraperMetrics]:
        """Retorna métricas de uma fonte específica."""
        return [m for m in self.metrics if m.source_id == source_id]
    
    def get_all_metrics(self) -> List[ScraperMetrics]:
        """Retorna todas as métricas."""
        return self.metrics
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calcula estatísticas gerais."""
        if not self.metrics:
            return {}
        
        total = len(self.metrics)
        avg_success_rate = sum(m.success_rate for m in self.metrics) / total
        avg_time = sum(m.time_seconds for m in self.metrics) / total
        total_errors = sum(len(m.errors) for m in self.metrics)
        paywall_detections = sum(1 for m in self.metrics if m.has_paywall_detected)
        
        # Por fonte
        by_source = {}
        for metrics in self.metrics:
            if metrics.source_id not in by_source:
                by_source[metrics.source_id] = []
            by_source[metrics.source_id].append(metrics)
        
        source_stats = {}
        for source_id, source_metrics in by_source.items():
            source_stats[source_id] = {
                "executions": len(source_metrics),
                "avg_success_rate": sum(m.success_rate for m in source_metrics) / len(source_metrics),
                "total_collected": sum(m.collected for m in source_metrics),
                "total_requested": sum(m.requested for m in source_metrics),
            }
        
        return {
            "total_executions": total,
            "avg_success_rate": avg_success_rate,
            "avg_time_seconds": avg_time,
            "total_errors": total_errors,
            "paywall_detections": paywall_detections,
            "by_source": source_stats,
        }
    
    def clear(self):
        """Limpa todas as métricas."""
        self.metrics.clear()
    
    def export_json(self) -> str:
        """Exporta métricas para JSON."""
        import json
        return json.dumps([m.to_dict() for m in self.metrics], indent=2)
