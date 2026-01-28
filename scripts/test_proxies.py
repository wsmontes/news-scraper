"""
Teste e demonstração do sistema de proxies.
"""

from news_scraper.proxy_manager import ProxyManager


def test_proxy_list():
    """Testa se temos proxies configurados."""
    manager = ProxyManager()
    
    print(f"Total de proxies: {len(manager.proxies)}")
    print("\nPrimeiros 5 proxies:")
    for i, proxy in enumerate(manager.proxies[:5], 1):
        print(f"  {i}. {proxy.url}")


def test_proxy_rotation():
    """Testa rotação de proxies."""
    manager = ProxyManager()
    
    print("Testando rotação (10 proxies):")
    for i in range(10):
        proxy = manager.get_next_proxy()
        if proxy:
            print(f"  {i+1}. {proxy.selenium_format}")


def test_proxy_connection():
    """Testa conexão real com proxies."""
    manager = ProxyManager()
    
    print("Testando conexão com proxies (pode demorar)...")
    print("Testando apenas os primeiros 5...\n")
    
    for i, proxy in enumerate(manager.proxies[:5], 1):
        print(f"{i}. Testando {proxy.url}... ", end="", flush=True)
        is_working = manager.test_proxy(proxy, timeout=3)
        status = "✅ OK" if is_working else "❌ FALHOU"
        print(status)


def test_with_browser():
    """Testa uso de proxy com browser."""
    from news_scraper.browser import BrowserConfig, ProfessionalScraper
    
    print("\nTestando proxy com browser...")
    print("Tentando acessar httpbin.org/ip (mostra seu IP)\n")
    
    # Sem proxy
    print("1. SEM PROXY:")
    config = BrowserConfig(headless=True, use_proxy=False)
    with ProfessionalScraper(config) as scraper:
        scraper.get_page("http://httpbin.org/ip", wait_time=2)
        html = scraper.driver.page_source
        if '"origin"' in html:
            import re
            ip = re.search(r'"origin":\s*"([^"]+)"', html)
            if ip:
                print(f"   IP detectado: {ip.group(1)}")
    
    # Com proxy
    print("\n2. COM PROXY:")
    config = BrowserConfig(headless=True, use_proxy=True, proxy_fallback=True)
    with ProfessionalScraper(config) as scraper:
        try:
            scraper.get_page("http://httpbin.org/ip", wait_time=2)
            html = scraper.driver.page_source
            if '"origin"' in html:
                import re
                ip = re.search(r'"origin":\s*"([^"]+)"', html)
                if ip:
                    print(f"   IP detectado: {ip.group(1)}")
                    print(f"   Proxy usado: {scraper.current_proxy.selenium_format if scraper.current_proxy else 'Nenhum'}")
        except Exception as e:
            print(f"   Erro: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("TESTE DO SISTEMA DE PROXIES")
    print("=" * 70)
    
    print("\n[1/4] Verificando lista de proxies...")
    test_proxy_list()
    
    print("\n" + "-" * 70)
    print("[2/4] Testando rotação...")
    test_proxy_rotation()
    
    print("\n" + "-" * 70)
    print("[3/4] Testando conexão (primeiros 5)...")
    test_proxy_connection()
    
    print("\n" + "-" * 70)
    print("[4/4] Testando com browser...")
    test_with_browser()
    
    print("\n" + "=" * 70)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 70)
