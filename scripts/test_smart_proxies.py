#!/usr/bin/env python3
"""
Testa sistema inteligente de proxies que aprende qual funciona melhor com cada site.
"""

from news_scraper.proxy_manager import ProxyManager
from news_scraper.browser import ProfessionalScraper, BrowserConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_learning_system():
    """Testa sistema de aprendizado de proxies."""
    print("\n" + "="*60)
    print("TESTE DO SISTEMA INTELIGENTE DE PROXIES")
    print("="*60)
    
    # Criar gerenciador com arquivo de estatísticas
    manager = ProxyManager(stats_file="data/proxy_stats.json")
    
    print(f"\n1. Proxies carregados: {len(manager.proxies)}")
    
    # Simular testes em diferentes sites
    domains = [
        "infomoney.com.br",
        "moneytimes.com.br", 
        "valor.globo.com",
        "bloomberg.com.br",
        "einvestidor.estadao.com.br"
    ]
    
    print("\n2. Testando proxies inteligentes por domínio:")
    print("-" * 60)
    
    for domain in domains:
        print(f"\n   Site: {domain}")
        
        # Pegar melhor proxy para o domínio
        best_proxy = manager.get_best_proxy_for_domain(domain)
        
        if best_proxy:
            rate = best_proxy.get_domain_success_rate(domain)
            print(f"   ✓ Melhor proxy: {best_proxy.selenium_format}")
            print(f"   ✓ Taxa de sucesso: {rate:.1%}")
            
            # Simular uso (na prática seria feito pelo scraper)
            # manager.mark_success(best_proxy, domain)
            # ou
            # manager.mark_failure(best_proxy, domain)
        else:
            print(f"   ⚠️ Nenhum proxy disponível")
    
    print("\n3. Estatísticas gerais:")
    print("-" * 60)
    for domain in domains[:2]:  # Mostrar detalhes de 2 sites
        stats = manager.get_domain_stats(domain)
        print(f"\n   {domain}:")
        print(f"   - Total de proxies: {stats['total_proxies']}")
        print(f"   - Proxies funcionando: {stats['working_proxies']}")
        print(f"   - Top 3 melhores:")
        
        for i, proxy_stat in enumerate(stats['best_proxies'][:3], 1):
            print(f"     {i}. {proxy_stat['proxy']}: {proxy_stat['success_rate']:.1%} "
                  f"({proxy_stat['attempts']} tentativas)")


def test_browser_integration():
    """Testa integração do sistema inteligente com browser."""
    print("\n" + "="*60)
    print("TESTE DE INTEGRAÇÃO COM BROWSER")
    print("="*60)
    
    config = BrowserConfig(
        headless=True,
        use_proxy=True,
        proxy_fallback=True
    )
    
    test_urls = [
        "https://www.infomoney.com.br/mercados/",
        "https://www.moneytimes.com.br/",
    ]
    
    for url in test_urls:
        print(f"\n1. Testando: {url}")
        
        try:
            with ProfessionalScraper(config) as scraper:
                # Usar melhor proxy para URL
                scraper.start_with_best_proxy_for_url(url)
                
                # Carregar página (vai aprender automaticamente)
                html = scraper.get_page(url, wait_time=2)
                
                print(f"   ✓ Página carregada: {len(html)} chars")
                
                if scraper.current_proxy:
                    print(f"   ✓ Proxy usado: {scraper.current_proxy.selenium_format}")
                else:
                    print(f"   ⚠️ Sem proxy (conexão direta)")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print("\n2. Sistema aprenderá automaticamente qual proxy funciona melhor!")
    print("   - Sucessos são salvos em data/proxy_stats.json")
    print("   - Próximas execuções usarão os melhores proxies")


def show_learning_progress():
    """Mostra progresso do aprendizado."""
    print("\n" + "="*60)
    print("PROGRESSO DO APRENDIZADO")
    print("="*60)
    
    manager = ProxyManager(stats_file="data/proxy_stats.json")
    
    print("\nTop 5 proxies por taxa de sucesso geral:")
    print("-" * 60)
    
    all_proxies = sorted(
        manager.proxies,
        key=lambda p: p.success_rate,
        reverse=True
    )
    
    for i, proxy in enumerate(all_proxies[:5], 1):
        total = proxy.successes + proxy.failures
        print(f"{i}. {proxy.selenium_format}")
        print(f"   - Taxa: {proxy.success_rate:.1%}")
        print(f"   - Tentativas: {total} ({proxy.successes}✓ / {proxy.failures}✗)")
        print(f"   - Domínios testados: {len(proxy.domain_stats)}")


if __name__ == "__main__":
    test_learning_system()
    print("\n" + "="*60)
    test_browser_integration()
    print("\n" + "="*60)
    show_learning_progress()
    print("\n" + "="*60)
    print("\n✓ Testes concluídos!")
    print("  Sistema aprende automaticamente qual proxy funciona melhor")
    print("  Estatísticas salvas em: data/proxy_stats.json")
