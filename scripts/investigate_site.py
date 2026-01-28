#!/usr/bin/env python3
"""
Script para investigar a estrutura de sites de notícias antes de criar scrapers especializados.

Uso:
    python scripts/investigate_site.py <URL>
"""

import sys
from news_scraper.browser import BrowserConfig, ProfessionalScraper


def investigate_site(url: str, headless: bool = True):
    """Investiga a estrutura de um site para entender como fazer scraping."""
    
    config = BrowserConfig(headless=headless)
    
    with ProfessionalScraper(config) as scraper:
        print(f"\n{'='*70}")
        print(f"Investigando: {url}")
        print(f"{'='*70}\n")
        
        # Carregar página
        print("[1/4] Carregando página...")
        scraper.get_page(url, wait_time=3)
        print(f"  ✓ Título: {scraper.driver.title}")
        print(f"  ✓ URL final: {scraper.driver.current_url}")
        
        # Scroll para carregar mais conteúdo
        print("\n[2/4] Scrolling para carregar conteúdo dinâmico...")
        scraper.scroll_and_load(scroll_pause=1.5, max_scrolls=2)
        print("  ✓ Scroll completo")
        
        # Analisar links
        print("\n[3/4] Analisando links...")
        all_links = scraper.driver.find_elements('css selector', 'a')
        print(f"  • Total de <a> tags: {len(all_links)}")
        
        # Filtrar possíveis artigos (URLs longas)
        article_candidates = []
        domain = url.split('/')[2]  # Extrair domínio
        
        for link in all_links:
            href = link.get_attribute('href')
            if href and domain in href and len(href) > 50:
                # Excluir navegação comum
                if not any(x in href.lower() for x in ['login', 'cadastro', 'subscribe', 'newsletter', 'author', 'tag', 'category']):
                    article_candidates.append(href)
        
        # Deduplicate
        article_candidates = sorted(set(article_candidates))
        
        print(f"  • Possíveis artigos (URLs longas): {len(article_candidates)}")
        
        # Mostrar exemplos
        print("\n[4/4] Exemplos de URLs de artigos:")
        for i, href in enumerate(article_candidates[:10], 1):
            print(f"  {i}. {href}")
        
        # Testar extração de um artigo
        if article_candidates:
            print(f"\n{'='*70}")
            print("Testando extração do primeiro artigo:")
            print(f"{'='*70}\n")
            
            test_url = article_candidates[0]
            print(f"URL: {test_url}\n")
            
            import requests
            from news_scraper.extract import extract_article
            
            try:
                response = requests.get(test_url, timeout=20, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                })
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    article = extract_article(test_url, response.text)
                    
                    print(f"\n✓ Título: {article.title or '(não extraído)'}")
                    print(f"✓ Autor: {article.author or '(não extraído)'}")
                    print(f"✓ Data: {article.date_published or '(não extraído)'}")
                    print(f"✓ Idioma: {article.language or '(não detectado)'}")
                    print(f"✓ Texto: {len(article.text) if article.text else 0} caracteres")
                    
                    if article.text:
                        print(f"\nPreview do texto:")
                        print(f"{article.text[:300]}...")
                    else:
                        print("\n⚠ Texto não foi extraído! Site pode precisar scraper especializado.")
                else:
                    print(f"⚠ Erro HTTP: {response.status_code}")
                    
            except Exception as e:
                print(f"⚠ Erro ao testar extração: {e}")
        
        print(f"\n{'='*70}")
        print("Resumo da investigação:")
        print(f"{'='*70}")
        print(f"• Site: {domain}")
        print(f"• URLs encontradas: {len(article_candidates)}")
        print(f"• Padrão de URL: {article_candidates[0] if article_candidates else 'N/A'}")
        
        if article_candidates:
            # Analisar padrão de URL
            sample_url = article_candidates[0]
            has_date = any(x in sample_url for x in ['/2024/', '/2025/', '/2026/'])
            has_slug = sample_url.count('/') > 3
            
            print(f"• Contém data na URL: {'Sim' if has_date else 'Não'}")
            print(f"• Tem slug descritivo: {'Sim' if has_slug else 'Não'}")
        
        print(f"\n{'='*70}")
        print("Próximo passo:")
        print(f"{'='*70}")
        
        if article_candidates:
            print("✓ Site parece acessível!")
            print("\nPara criar scraper especializado:")
            print(f"1. Analisar padrão das URLs acima")
            print(f"2. Testar extração em mais artigos")
            print(f"3. Identificar seletores CSS específicos se necessário")
            print(f"4. Criar módulo em src/news_scraper/<site>_scraper.py")
        else:
            print("⚠ Nenhum artigo encontrado!")
            print("  - Tente ajustar os filtros")
            print("  - Verifique se o site usa JavaScript pesado")
            print("  - Inspecione manualmente no navegador")
        
        if not headless:
            input("\nPressione Enter para fechar o navegador...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/investigate_site.py <URL>")
        print("\nExemplos:")
        print("  python scripts/investigate_site.py https://www.infomoney.com.br/")
        print("  python scripts/investigate_site.py https://www.businessinsider.com/br")
        print("  python scripts/investigate_site.py https://valor.globo.com/")
        sys.exit(1)
    
    url = sys.argv[1]
    headless = '--no-headless' not in sys.argv
    
    try:
        investigate_site(url, headless=headless)
    except KeyboardInterrupt:
        print("\n\n❌ Investigação interrompida.")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
