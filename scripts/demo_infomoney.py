#!/usr/bin/env python3
"""
Exemplo completo: Coleta de notícias do InfoMoney com browser scraping

Demonstra o fluxo profissional:
1. Browser scraping para extrair URLs
2. Scraping de conteúdo
3. Salvamento em Parquet
4. Consulta SQL

Uso:
    python scripts/demo_infomoney.py
"""

from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.scrape import scrape_urls
from pathlib import Path


def extract_urls(limit: int = 20) -> list[str]:
    """Extrai URLs de artigos do InfoMoney usando browser scraping."""
    
    print("=" * 70)
    print("ETAPA 1: Extração de URLs com Browser Scraping (Selenium)")
    print("=" * 70)
    
    config = BrowserConfig(headless=True)
    
    with ProfessionalScraper(config) as scraper:
        print("\n[1/3] Carregando homepage do InfoMoney...")
        scraper.get_page('https://www.infomoney.com.br/', wait_time=3)
        print("      ✓ Página carregada")
        
        print("\n[2/3] Scrolling para carregar conteúdo dinâmico...")
        scraper.scroll_and_load(scroll_pause=1.5, max_scrolls=3)
        print("      ✓ Scroll completo")
        
        print("\n[3/3] Extraindo links de artigos...")
        all_links = scraper.driver.find_elements('css selector', 'a')
        
        article_urls = []
        for link in all_links:
            href = link.get_attribute('href')
            # Filtrar apenas artigos de mercados (URLs longas = artigos)
            if href and '/mercados/' in href and len(href) > 60:
                article_urls.append(href)
        
        # Deduplicate e limitar
        article_urls = sorted(set(article_urls))[:limit]
        
        print(f"      ✓ {len(article_urls)} URLs únicas encontradas")
        
        return article_urls


def save_and_scrape(urls: list[str], dataset_dir: str = "data/processed/articles") -> None:
    """Salva URLs e faz scraping para dataset Parquet."""
    
    # Salvar URLs
    urls_file = Path("data/raw/infomoney_demo.txt")
    urls_file.parent.mkdir(parents=True, exist_ok=True)
    urls_file.write_text("\n".join(urls) + "\n", encoding="utf-8")
    print(f"\n✓ URLs salvas em {urls_file}")
    
    print("\n" + "=" * 70)
    print("ETAPA 2: Scraping de Conteúdo")
    print("=" * 70)
    print(f"\nIniciando scraping de {len(urls)} artigos...")
    print("(delay de 2s entre requisições para ser polido)")
    
    # Scraping com salvamento direto em Parquet
    scrape_urls(
        urls,
        out_path=None,  # Não salvar JSONL
        dataset_dir=Path(dataset_dir),
        delay_seconds=2.0,
        timeout_seconds=20.0,
        respect_robots=True,
    )
    
    print(f"\n✓ Scraping completo! Dataset salvo em: {dataset_dir}/")


def query_dataset(dataset_dir: str = "data/processed/articles") -> None:
    """Consulta o dataset usando DuckDB."""
    
    print("\n" + "=" * 70)
    print("ETAPA 3: Consulta SQL no Dataset Parquet")
    print("=" * 70)
    
    import duckdb
    
    conn = duckdb.connect(database=':memory:')
    
    # Query 1: Estatísticas gerais
    print("\n[Query 1] Estatísticas gerais:")
    result = conn.execute(f"""
        SELECT 
            COUNT(*) as total_artigos,
            COUNT(DISTINCT source) as total_fontes
        FROM read_parquet('{dataset_dir}/**/*.parquet')
    """).fetchone()
    print(f"  • Total de artigos: {result[0]}")
    print(f"  • Fontes únicas: {result[1]}")
    
    # Query 2: Títulos e tamanhos
    print("\n[Query 2] Títulos e tamanhos de texto:")
    result = conn.execute(f"""
        SELECT 
            title,
            LENGTH(text) as chars
        FROM read_parquet('{dataset_dir}/**/*.parquet')
        LIMIT 5
    """).fetchall()
    
    for i, (title, chars) in enumerate(result, 1):
        print(f"\n  {i}. {title}")
        print(f"     ({chars:,} caracteres)")
    
    # Query 3: Preview de texto
    print("\n[Query 3] Preview do primeiro artigo:")
    result = conn.execute(f"""
        SELECT text
        FROM read_parquet('{dataset_dir}/**/*.parquet')
        LIMIT 1
    """).fetchone()
    
    if result and result[0]:
        preview = result[0][:300]
        print(f"\n  {preview}...")
    
    conn.close()


def main():
    """Executa o exemplo completo."""
    
    print("\n🚀 DEMO: News Scraper Profissional - InfoMoney")
    print("=" * 70)
    print("\nEste script demonstra o fluxo completo de coleta de notícias:")
    print("1. Browser scraping (Selenium) para extrair URLs")
    print("2. Scraping polido com delays adequados")
    print("3. Salvamento em dataset Parquet particionado")
    print("4. Consultas SQL com DuckDB")
    print("\n" + "=" * 70)
    
    # Parâmetros
    NUM_ARTICLES = 10  # Número de artigos para demo
    DATASET_DIR = "data/processed/articles"
    
    input("\nPressione Enter para iniciar a demo...")
    
    # Etapa 1: Extrair URLs
    urls = extract_urls(limit=NUM_ARTICLES)
    
    if not urls:
        print("\n❌ Erro: Nenhuma URL foi extraída.")
        print("   Possíveis causas:")
        print("   - InfoMoney mudou estrutura do site")
        print("   - Problemas de conectividade")
        print("   - ChromeDriver não instalado")
        return
    
    # Etapa 2: Scraping
    save_and_scrape(urls, DATASET_DIR)
    
    # Etapa 3: Consultas
    query_dataset(DATASET_DIR)
    
    print("\n" + "=" * 70)
    print("✅ DEMO CONCLUÍDA!")
    print("=" * 70)
    print(f"\nDataset disponível em: {DATASET_DIR}/")
    print("\nPróximos passos:")
    print("  1. Explorar com: news-scraper query --dataset-dir {DATASET_DIR} --sql 'SELECT * FROM articles'")
    print("  2. Exportar para CSV: news-scraper query ... --format csv > export.csv")
    print("  3. Aplicar análise de sentimento em Python com transformers")
    print("  4. Correlacionar com eventos financeiros históricos")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Demo interrompida pelo usuário.")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
