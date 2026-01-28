"""
Gerenciador de proxies gratuitos com fallback automático e aprendizado.

Mantém lista de 20+ proxies públicos, rotaciona entre eles
e aprende quais funcionam melhor para cada site.
"""

from __future__ import annotations
import random
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProxyInfo:
    """Informações de um proxy."""
    host: str
    port: int
    protocol: str = "http"
    working: bool = True
    failures: int = 0
    successes: int = 0
    # Estatísticas por domínio
    domain_stats: Dict[str, Dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: {"success": 0, "failure": 0}))
    
    @property
    def url(self) -> str:
        """Retorna URL completa do proxy."""
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def selenium_format(self) -> str:
        """Formato para Selenium."""
        return f"{self.host}:{self.port}"
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso geral."""
        total = self.successes + self.failures
        if total == 0:
            return 0.5  # Neutro se nunca usado
        return self.successes / total
    
    def get_domain_success_rate(self, domain: str) -> float:
        """Taxa de sucesso para domínio específico."""
        stats = self.domain_stats.get(domain, {"success": 0, "failure": 0})
        total = stats["success"] + stats["failure"]
        if total == 0:
            return self.success_rate  # Usar taxa geral se nunca testado neste domínio
        return stats["success"] / total
    
    def record_success(self, domain: Optional[str] = None):
        """Registra sucesso."""
        self.successes += 1
        self.failures = max(0, self.failures - 1)  # Reduz falhas
        self.working = True
        
        if domain:
            if domain not in self.domain_stats:
                self.domain_stats[domain] = {"success": 0, "failure": 0}
            self.domain_stats[domain]["success"] += 1
    
    def record_failure(self, domain: Optional[str] = None):
        """Registra falha."""
        self.failures += 1
        
        if domain:
            if domain not in self.domain_stats:
                self.domain_stats[domain] = {"success": 0, "failure": 0}
            self.domain_stats[domain]["failure"] += 1


class ProxyManager:
    """Gerenciador de proxies com rotação, fallback e aprendizado."""
    
    # Lista de proxies públicos gratuitos
    # Fonte: https://www.free-proxy-list.net/, https://spys.one/en/
    FREE_PROXIES = [
        # Brasil
        ("200.155.139.242", 3128),
        ("191.252.103.16", 80),
        ("200.174.198.86", 8888),
        ("177.93.50.171", 999),
        ("45.71.115.211", 999),
        
        # EUA
        ("64.225.8.192", 9991),
        ("157.230.34.219", 3128),
        ("165.232.129.150", 80),
        ("104.248.90.212", 80),
        ("167.71.5.83", 3128),
        
        # Europa
        ("91.229.114.63", 80),
        ("185.162.230.55", 80),
        ("51.159.115.233", 3128),
        ("195.154.255.118", 8080),
        ("141.94.104.25", 8080),
        
        # Ásia
        ("103.152.112.162", 80),
        ("103.155.196.47", 8181),
        ("43.134.68.153", 3128),
        ("47.88.62.42", 80),
        ("103.163.51.254", 80),
        
        # América Latina
        ("190.61.88.147", 8080),
        ("181.129.74.58", 40667),
        ("186.148.102.43", 8083),
        ("200.105.215.22", 33630),
        ("201.218.91.13", 999),
    ]
    
    def __init__(self, max_failures: int = 3, stats_file: Optional[str] = None):
        """
        Args:
            max_failures: Número máximo de falhas antes de marcar proxy como não funcional
            stats_file: Arquivo para persistir estatísticas (None = padrão data/proxy_stats.json)
        """
        self.max_failures = max_failures
        self.proxies: List[ProxyInfo] = []
        self.current_index = 0
        self.stats_file = Path(stats_file) if stats_file else Path("data/proxy_stats.json")
        self._initialize_proxies()
        self._load_stats()
    
    def _initialize_proxies(self) -> None:
        """Inicializa lista de proxies."""
        self.proxies = [
            ProxyInfo(host=host, port=port)
            for host, port in self.FREE_PROXIES
        ]
        random.shuffle(self.proxies)
        logger.info(f"Inicializados {len(self.proxies)} proxies")
    
    def _load_stats(self) -> None:
        """Carrega estatísticas salvas."""
        if not self.stats_file.exists():
            return
        
        try:
            with open(self.stats_file, 'r') as f:
                data = json.load(f)
            
            for proxy in self.proxies:
                key = proxy.selenium_format
                if key in data:
                    proxy.successes = data[key].get("successes", 0)
                    proxy.failures = data[key].get("failures", 0)
                    proxy.domain_stats = defaultdict(
                        lambda: {"success": 0, "failure": 0},
                        data[key].get("domain_stats", {})
                    )
            
            logger.info(f"Estatísticas carregadas de {self.stats_file}")
        except Exception as e:
            logger.warning(f"Erro ao carregar estatísticas: {e}")
    
    def _save_stats(self) -> None:
        """Salva estatísticas."""
        try:
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {}
            for proxy in self.proxies:
                key = proxy.selenium_format
                data[key] = {
                    "successes": proxy.successes,
                    "failures": proxy.failures,
                    "domain_stats": dict(proxy.domain_stats)
                }
            
            with open(self.stats_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Estatísticas salvas em {self.stats_file}")
        except Exception as e:
            logger.warning(f"Erro ao salvar estatísticas: {e}")
    
    def get_best_proxy_for_domain(self, domain: str, min_success_rate: float = 0.3) -> Optional[ProxyInfo]:
        """
        Retorna melhor proxy para um domínio específico baseado em histórico.
        
        Args:
            domain: Domínio (ex: 'infomoney.com.br')
            min_success_rate: Taxa mínima de sucesso (0.0-1.0)
            
        Returns:
            ProxyInfo com melhor histórico para o domínio
        """
        working_proxies = [p for p in self.proxies if p.working]
        
        if not working_proxies:
            self._reset_failures()
            working_proxies = self.proxies
        
        # Ordenar por taxa de sucesso no domínio específico
        scored_proxies = [
            (proxy, proxy.get_domain_success_rate(domain))
            for proxy in working_proxies
        ]
        scored_proxies.sort(key=lambda x: x[1], reverse=True)
        
        # Filtrar por taxa mínima
        viable = [p for p, rate in scored_proxies if rate >= min_success_rate]
        
        if viable:
            # 80% melhor, 20% exploração
            if random.random() < 0.8:
                return viable[0]
            else:
                return random.choice(working_proxies)
        
        # Nenhum viável, retornar melhor disponível
        return scored_proxies[0][0] if scored_proxies else None
    
    def get_next_proxy(self) -> Optional[ProxyInfo]:
        """
        Retorna próximo proxy da rotação.
        
        Returns:
            ProxyInfo ou None se não houver proxies disponíveis
        """
        working_proxies = [p for p in self.proxies if p.working]
        
        if not working_proxies:
            logger.warning("Nenhum proxy funcional, resetando contadores")
            self._reset_failures()
            working_proxies = self.proxies
        
        if not working_proxies:
            return None
        
        # Rotaciona pelo índice
        self.current_index = (self.current_index + 1) % len(working_proxies)
        return working_proxies[self.current_index]
    
    def mark_failure(self, proxy: ProxyInfo, domain: Optional[str] = None) -> None:
        """
        Marca proxy como falho.
        
        Args:
            proxy: Proxy que falhou
            domain: Domínio onde falhou (para estatísticas)
        """
        proxy.record_failure(domain)
        
        if proxy.failures >= self.max_failures:
            proxy.working = False
            logger.warning(f"Proxy {proxy.url} marcado como não funcional")
        
        self._save_stats()
    
    def mark_success(self, proxy: ProxyInfo, domain: Optional[str] = None) -> None:
        """
        Marca proxy como bem-sucedido.
        
        Args:
            proxy: Proxy que funcionou
            domain: Domínio onde funcionou (para estatísticas)
        """
        proxy.record_success(domain)
        self._save_stats()
    
    def _reset_failures(self) -> None:
        """Reseta contadores de falha de todos os proxies."""
        for proxy in self.proxies:
            proxy.failures = 0
            proxy.working = True
        logger.info("Contadores de falha resetados")
    
    def test_proxy(self, proxy: ProxyInfo, timeout: int = 5) -> bool:
        """
        Testa se um proxy está funcionando.
        
        Args:
            proxy: Proxy para testar
            timeout: Timeout em segundos
            
        Returns:
            True se proxy está funcionando
        """
        try:
            proxies = {
                "http": proxy.url,
                "https": proxy.url,
            }
            response = requests.get(
                "http://www.google.com",
                proxies=proxies,
                timeout=timeout
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Proxy {proxy.url} falhou no teste: {e}")
            return False
    
    def test_all_proxies(self, timeout: int = 5) -> Dict[str, int]:
        """
        Testa todos os proxies e retorna estatísticas.
        
        Args:
            timeout: Timeout em segundos por proxy
            
        Returns:
            Dicionário com estatísticas
        """
        working = 0
        failed = 0
        
        for proxy in self.proxies:
            if self.test_proxy(proxy, timeout):
                working += 1
                self.mark_success(proxy)
            else:
                failed += 1
                self.mark_failure(proxy)
        
        stats = {
            "total": len(self.proxies),
            "working": working,
            "failed": failed,
            "success_rate": working / len(self.proxies) if self.proxies else 0
        }
        
        logger.info(f"Teste de proxies: {stats}")
        return stats
    
    def get_random_proxy(self) -> Optional[ProxyInfo]:
        """
        Retorna um proxy aleatório da lista de funcionais.
        
        Returns:
            ProxyInfo ou None
        """
        working_proxies = [p for p in self.proxies if p.working]
        
        if not working_proxies:
            self._reset_failures()
            working_proxies = self.proxies
        
        return random.choice(working_proxies) if working_proxies else None
    
    def get_selenium_proxy_arg(self, proxy: Optional[ProxyInfo] = None) -> str:
        """
        Retorna argumento de proxy formatado para Selenium.
        
        Args:
            proxy: Proxy específico ou None para pegar o próximo
            
        Returns:
            String no formato "--proxy-server=host:port"
        """
        if proxy is None:
            proxy = self.get_next_proxy()
        
        if proxy is None:
            return ""
        
        return f"--proxy-server={proxy.selenium_format}"
    
    def get_requests_proxy_dict(self, proxy: Optional[ProxyInfo] = None) -> Dict[str, str]:
        """
        Retorna dicionário de proxy formatado para requests.
        
        Args:
            proxy: Proxy específico ou None para pegar o próximo
            
        Returns:
            Dicionário com formato {"http": "url", "https": "url"}
        """
        if proxy is None:
            proxy = self.get_next_proxy()
        
        if proxy is None:
            return {}
        
        return {
            "http": proxy.url,
            "https": proxy.url,
        }
    
    def get_domain_stats(self, domain: str) -> Dict[str, any]:
        """
        Retorna estatísticas de proxies para um domínio.
        
        Args:
            domain: Domínio para consultar
            
        Returns:
            Dicionário com estatísticas
        """
        stats = []
        for proxy in self.proxies:
            rate = proxy.get_domain_success_rate(domain)
            domain_total = 0
            if domain in proxy.domain_stats:
                domain_total = proxy.domain_stats[domain]["success"] + proxy.domain_stats[domain]["failure"]
            
            stats.append({
                "proxy": proxy.selenium_format,
                "success_rate": rate,
                "attempts": domain_total,
                "working": proxy.working
            })
        
        # Ordenar por taxa de sucesso
        stats.sort(key=lambda x: x["success_rate"], reverse=True)
        
        return {
            "domain": domain,
            "total_proxies": len(self.proxies),
            "working_proxies": sum(1 for p in self.proxies if p.working),
            "best_proxies": stats[:5],
            "all_stats": stats
        }


# Instância global
_proxy_manager: Optional[ProxyManager] = None


def get_proxy_manager() -> ProxyManager:
    """Retorna instância global do proxy manager."""
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = ProxyManager()
    return _proxy_manager
