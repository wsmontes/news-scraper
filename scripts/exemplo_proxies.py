"""
Exemplo de uso do sistema de proxies com scrapers.
"""

from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.sources.pt import InfoMoneyScraper


def scrape_without_proxy():
    """Scraping tradicional sem proxy."""
    print("🔵 Scraping SEM proxy...")
    
    config = BrowserConfig(headless=True, use_proxy=False)
    
    with ProfessionalScraper(config) as scraper:
        infomoney = InfoMoneyScraper(scraper)
        urls = infomoney.get_latest_articles(limit=3)
        
        print(f"   ✅ {len(urls)} URLs coletadas")
        for url in urls[:2]:
            print(f"      - {url[:70]}...")


def scrape_with_proxy():
    """Scraping com proxy e fallback automático."""
    print("\n🟢 Scraping COM proxy (fallback automático)...")
    
    config = BrowserConfig(
        headless=True,
        use_proxy=True,
        proxy_fallback=True
    )
    
    with ProfessionalScraper(config) as scraper:
        infomoney = InfoMoneyScraper(scraper)
        
        if scraper.current_proxy:
            print(f"   📡 Proxy: {scraper.current_proxy.selenium_format}")
        
        try:
            urls = infomoney.get_latest_articles(limit=3)
            print(f"   ✅ {len(urls)} URLs coletadas")
            for url in urls[:2]:
                print(f"      - {url[:70]}...")
        except Exception as e:
            print(f"   ❌ Erro: {e}")


def scrape_with_proxy_rotation():
    """Scraping com múltiplos proxies (rotação)."""
    print("\n🔄 Scraping com ROTAÇÃO de proxies...")
    
    from news_scraper.proxy_manager import get_proxy_manager
    
    proxy_manager = get_proxy_manager()
    
    # Testar com 3 proxies diferentes
    for i in range(3):
        proxy = proxy_manager.get_next_proxy()
        if not proxy:
            print(f"   ❌ Tentativa {i+1}: Sem proxies disponíveis")
            continue
        
        print(f"\n   Tentativa {i+1} - Proxy: {proxy.selenium_format}")
        
        config = BrowserConfig(headless=True, use_proxy=True, proxy_fallback=False)
        
        try:
            with ProfessionalScraper(config) as scraper:
                scraper.current_proxy = proxy
                infomoney = InfoMoneyScraper(scraper)
                urls = infomoney.get_latest_articles(limit=2)
                
                proxy_manager.mark_success(proxy)
                print(f"      ✅ {len(urls)} URLs coletadas")
        except Exception as e:
            proxy_manager.mark_failure(proxy)
            print(f"      ❌ Falhou: {str(e)[:50]}")


if __name__ == "__main__":
    print("=" * 70)
    print("EXEMPLO: SCRAPING COM PROXIES")
    print("=" * 70)
    
    # 1. Sem proxy (padrão)
    scrape_without_proxy()
    
    # 2. Com proxy + fallback
    scrape_with_proxy()
    
    # 3. Rotação manual
    scrape_with_proxy_rotation()
    
    print("\n" + "=" * 70)
    print("💡 DICAS:")
    print("   - use_proxy=True: Ativa proxies")
    print("   - proxy_fallback=True: Tenta sem proxy se todos falharem")
    print("   - ProxyManager rotaciona automaticamente entre 25 proxies")
    print("   - Proxies que falham 3x são marcados como indisponíveis")
    print("=" * 70)
