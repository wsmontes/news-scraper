"""
Exemplo de uso completo dos scrapers de fontes financeiras.

Este script demonstra como coletar notícias de todas as fontes,
extrair metadados completos e salvar em formato estruturado.

Execute: python scripts/exemplo_todas_fontes.py
"""

from datetime import datetime
import json
from pathlib import Path
from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.infomoney_scraper import InfoMoneyScraper
from news_scraper.valor_scraper import ValorScraper
from news_scraper.bloomberg_scraper import BloombergScraper
from news_scraper.einvestidor_scraper import EInvestidorScraper
from news_scraper.moneytimes_scraper import MoneyTimesScraper
from news_scraper.extract import extract_article_metadata


def collect_from_all_sources(limit_per_source: int = 5):
    """
    Coleta notícias de todas as fontes disponíveis.
    
    Args:
        limit_per_source: Número de artigos por fonte
    
    Returns:
        Lista de artigos com metadados completos
    """
    config = BrowserConfig(headless=True)
    articles = []
    
    with ProfessionalScraper(config) as scraper:
        print("🚀 Iniciando coleta multi-fonte...")
        print(f"📊 Meta: {limit_per_source} artigos por fonte\n")
        
        # InfoMoney
        print("📰 [1/5] InfoMoney...")
        infomoney = InfoMoneyScraper(scraper)
        urls = infomoney.get_latest_articles(limit=limit_per_source)
        print(f"   ✓ {len(urls)} URLs coletadas")
        
        for i, url in enumerate(urls, 1):
            print(f"   [{i}/{len(urls)}] Extraindo metadados...")
            scraper.get_page(url, wait_time=2)
            article = extract_article_metadata(url, scraper.driver)
            articles.append(article)
        
        # Valor Econômico
        print("\n📰 [2/5] Valor Econômico...")
        valor = ValorScraper(scraper)
        urls = valor.get_latest_articles(limit=limit_per_source)
        print(f"   ✓ {len(urls)} URLs coletadas")
        
        for i, url in enumerate(urls, 1):
            print(f"   [{i}/{len(urls)}] Extraindo metadados...")
            scraper.get_page(url, wait_time=2)
            article = extract_article_metadata(url, scraper.driver)
            articles.append(article)
        
        # Bloomberg Brasil
        print("\n📰 [3/5] Bloomberg Brasil...")
        bloomberg = BloombergScraper(scraper)
        urls = bloomberg.get_latest_articles(limit=limit_per_source)
        print(f"   ✓ {len(urls)} URLs coletadas")
        
        for i, url in enumerate(urls, 1):
            print(f"   [{i}/{len(urls)}] Extraindo metadados...")
            scraper.get_page(url, wait_time=2)
            article = extract_article_metadata(url, scraper.driver)
            articles.append(article)
        
        # E-Investidor
        print("\n📰 [4/5] E-Investidor (Estadão)...")
        einvestidor = EInvestidorScraper(scraper)
        urls = einvestidor.get_latest_articles(limit=limit_per_source)
        print(f"   ✓ {len(urls)} URLs coletadas")
        
        for i, url in enumerate(urls, 1):
            print(f"   [{i}/{len(urls)}] Extraindo metadados...")
            scraper.get_page(url, wait_time=2)
            article = extract_article_metadata(url, scraper.driver)
            articles.append(article)
        
        # Money Times
        print("\n📰 [5/5] Money Times...")
        moneytimes = MoneyTimesScraper(scraper)
        urls = moneytimes.get_latest_articles(limit=limit_per_source)
        print(f"   ✓ {len(urls)} URLs coletadas")
        
        for i, url in enumerate(urls, 1):
            print(f"   [{i}/{len(urls)}] Extraindo metadados...")
            scraper.get_page(url, wait_time=2)
            article = extract_article_metadata(url, scraper.driver)
            articles.append(article)
    
    return articles


def save_articles(articles, output_file: str = "data/raw/todas_fontes.jsonl"):
    """
    Salva artigos em formato JSONL.
    
    Args:
        articles: Lista de artigos (Article objects)
        output_file: Caminho do arquivo de saída
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for article in articles:
            article_dict = {
                'url': article.url,
                'title': article.title,
                'author': article.author,
                'date_published': article.date_published.isoformat() if article.date_published else None,
                'scraped_at': article.scraped_at.isoformat() if article.scraped_at else None,
                'text': article.text,
                'text_length': len(article.text) if article.text else 0,
                'language': article.language,
                'source': article.source,
                'extra': article.extra,
            }
            f.write(json.dumps(article_dict, ensure_ascii=False) + '\n')
    
    print(f"\n💾 Artigos salvos em: {output_path}")


def print_statistics(articles):
    """Imprime estatísticas da coleta."""
    print("\n" + "=" * 70)
    print("📊 ESTATÍSTICAS DA COLETA")
    print("=" * 70)
    
    total = len(articles)
    with_title = sum(1 for a in articles if a.title)
    with_date = sum(1 for a in articles if a.date_published)
    with_author = sum(1 for a in articles if a.author)
    with_text = sum(1 for a in articles if a.text and len(a.text) > 100)
    
    # Por fonte
    sources = {}
    for article in articles:
        source = article.source or "Desconhecida"
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\n📄 Total de artigos: {total}")
    print(f"\n✅ Campos extraídos:")
    print(f"   Título:  {with_title:3d} ({with_title/total*100:5.1f}%)")
    print(f"   Data:    {with_date:3d} ({with_date/total*100:5.1f}%)")
    print(f"   Autor:   {with_author:3d} ({with_author/total*100:5.1f}%)")
    print(f"   Texto:   {with_text:3d} ({with_text/total*100:5.1f}%)")
    
    print(f"\n🏷️  Por fonte:")
    for source, count in sorted(sources.items()):
        print(f"   {source:25} {count:3d} artigos")
    
    # Tamanho médio do texto
    text_lengths = [len(a.text) for a in articles if a.text]
    if text_lengths:
        avg_length = sum(text_lengths) / len(text_lengths)
        print(f"\n📝 Tamanho médio do texto: {avg_length:,.0f} caracteres")
    
    print("=" * 70)


def main():
    """Função principal."""
    print("=" * 70)
    print("🎯 COLETA MULTI-FONTE DE NOTÍCIAS FINANCEIRAS")
    print("=" * 70)
    print("\nFontes:")
    print("  1. InfoMoney")
    print("  2. Valor Econômico")
    print("  3. Bloomberg Brasil")
    print("  4. E-Investidor (Estadão)")
    print("  5. Money Times")
    print()
    
    # Coletar artigos
    articles = collect_from_all_sources(limit_per_source=3)
    
    # Estatísticas
    print_statistics(articles)
    
    # Salvar
    save_articles(articles)
    
    print("\n✅ Processo concluído!")
    print("\n💡 Próximos passos:")
    print("   - Carregar artigos: json.load('data/raw/todas_fontes.jsonl')")
    print("   - Análise de sentimento com FinBERT-PT-BR")
    print("   - Correlação com eventos financeiros")


if __name__ == "__main__":
    main()
