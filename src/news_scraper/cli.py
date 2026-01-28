from __future__ import annotations

import argparse
from pathlib import Path

from .browser import BrowserConfig, ProfessionalScraper
from .historical import generate_urls_by_date_pattern, generate_urls_by_month_pattern
from .query import dataset_stats, query_dataset
from .rss import collect_links_from_feed
from .scrape import scrape_urls
from .sitemap import extract_urls_from_archive_page, save_sitemap_urls
from .sources import enabled_rss_feeds, load_sources_csv
from .sources_cli import add_source, list_sources, toggle_source
from .yahoo_finance import YahooFinanceScraper


def _read_urls_from_file(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8")
    urls: list[str] = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def _write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="news-scraper", description="Scraper acadêmico de notícias")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scrape", help="Extrai notícias a partir de URLs")
    s.add_argument("--url", action="append", default=[], help="URL do artigo (pode repetir)")
    s.add_argument("--input", type=Path, help="Arquivo com URLs (1 por linha)")
    s.add_argument("--out", type=Path, required=False, help="Arquivo de saída (.jsonl ou .csv)")
    s.add_argument("--format", choices=["jsonl", "csv"], default="jsonl")
    s.add_argument(
        "--dataset-dir",
        type=Path,
        required=False,
        help="Diretório do dataset Parquet particionado (ex.: data/processed/articles)",
    )
    s.add_argument("--delay", type=float, default=1.0, help="Delay por domínio (segundos)")
    s.add_argument("--timeout", type=float, default=20.0, help="Timeout HTTP (segundos)")
    s.add_argument("--no-respect-robots", action="store_true", help="Ignora robots.txt")
    s.add_argument("--user-agent", type=str, default=None)
    s.add_argument("--max", type=int, default=None, help="Máximo de artigos")

    r = sub.add_parser("rss", help="Coleta links de RSS e opcionalmente raspa")
    r.add_argument("--feed", action="append", default=[], required=False, help="URL do RSS (pode repetir)")
    r.add_argument(
        "--sources-csv",
        type=Path,
        required=False,
        help="CSV com fontes (usa linhas enabled=1 e type=rss)",
    )
    r.add_argument("--limit", type=int, default=None, help="Limite por feed")
    r.add_argument("--out", type=Path, required=False, help="Saída: .txt (links) ou .jsonl/.csv (se --scrape)")
    r.add_argument("--scrape", action="store_true", help="Após coletar, raspar os links")
    r.add_argument("--format", choices=["jsonl", "csv"], default="jsonl")
    r.add_argument(
        "--dataset-dir",
        type=Path,
        required=False,
        help="Diretório do dataset Parquet particionado (ex.: data/processed/articles)",
    )
    r.add_argument("--delay", type=float, default=1.0)
    r.add_argument("--timeout", type=float, default=20.0)
    r.add_argument("--no-respect-robots", action="store_true")
    r.add_argument("--user-agent", type=str, default=None)
    r.add_argument("--max", type=int, default=None, help="Máximo total de artigos")

    q = sub.add_parser("query", help="Executa SQL no dataset Parquet (DuckDB)")
    q.add_argument(
        "--dataset-dir",
        type=Path,
        required=True,
        help="Diretório do dataset Parquet",
    )
    q.add_argument("--sql", type=str, required=True, help="Query SQL (use 'articles' como tabela)")
    q.add_argument(
        "--format",
        choices=["table", "csv", "json"],
        default="table",
        help="Formato de saída",
    )

    st = sub.add_parser("stats", help="Estatísticas do dataset")
    st.add_argument(
        "--dataset-dir",
        type=Path,
        required=True,
        help="Diretório do dataset Parquet",
    )

    src = sub.add_parser("sources", help="Gerencia fontes (sources.csv)")
    src_sub = src.add_subparsers(dest="sources_cmd", required=True)

    src_list = src_sub.add_parser("list", help="Lista fontes")
    src_list.add_argument(
        "--csv",
        type=Path,
        default=Path("configs/sources.csv"),
        help="Caminho do CSV",
    )

    src_add = src_sub.add_parser("add", help="Adiciona fonte")
    src_add.add_argument(
        "--csv",
        type=Path,
        default=Path("configs/sources.csv"),
        help="Caminho do CSV",
    )
    src_add.add_argument("--id", type=str, required=True, help="ID da fonte")
    src_add.add_argument("--name", type=str, required=True, help="Nome da fonte")
    src_add.add_argument("--type", type=str, required=True, help="Tipo (ex.: rss)")
    src_add.add_argument("--url", type=str, required=True, help="URL do feed/sitemap")
    src_add.add_argument("--tags", type=str, default=None, help="Tags separadas por ;")
    src_add.add_argument("--disabled", action="store_true", help="Adicionar desabilitada")

    src_enable = src_sub.add_parser("enable", help="Habilita fonte")
    src_enable.add_argument(
        "--csv",
        type=Path,
        default=Path("configs/sources.csv"),
        help="Caminho do CSV",
    )
    src_enable.add_argument("id", type=str, help="ID da fonte")

    src_disable = src_sub.add_parser("disable", help="Desabilita fonte")
    src_disable.add_argument(
        "--csv",
        type=Path,
        default=Path("configs/sources.csv"),
        help="Caminho do CSV",
    )
    src_disable.add_argument("id", type=str, help="ID da fonte")

    hist = sub.add_parser("historical", help="Ferramentas para coleta histórica")
    hist_sub = hist.add_subparsers(dest="hist_cmd", required=True)

    hist_gen = hist_sub.add_parser("generate", help="Gera URLs por padrão de data")
    hist_gen.add_argument(
        "--pattern",
        type=str,
        required=True,
        help="Padrão de URL (ex.: https://site.com/arquivo/{YYYY}/{MM}/{DD}/)",
    )
    hist_gen.add_argument("--start", type=str, required=True, help="Data inicial (YYYY-MM-DD)")
    hist_gen.add_argument("--end", type=str, required=True, help="Data final (YYYY-MM-DD)")
    hist_gen.add_argument("--out", type=Path, required=True, help="Arquivo de saída (.txt)")
    hist_gen.add_argument(
        "--by-month",
        action="store_true",
        help="Gerar por mês ao invés de por dia",
    )

    hist_sitemap = hist_sub.add_parser("sitemap", help="Extrai URLs de sitemap XML")
    hist_sitemap.add_argument("--url", type=str, required=True, help="URL do sitemap")
    hist_sitemap.add_argument("--out", type=Path, required=True, help="Arquivo de saída (.txt)")
    hist_sitemap.add_argument(
        "--filter",
        type=str,
        default=None,
        help="Filtrar URLs que contenham este texto",
    )

    hist_archive = hist_sub.add_parser("archive", help="Extrai links de página de arquivo")
    hist_archive.add_argument(
        "--url",
        type=str,
        required=True,
        help="URL da página de arquivo",
    )
    hist_archive.add_argument("--out", type=Path, required=True, help="Arquivo de saída (.txt)")

    # Comando collect - unificado e completo
    collect = sub.add_parser(
        "collect",
        help="Coleta notícias de fontes financeiras (modo completo)"
    )
    collect.add_argument(
        "--source",
        action="append",
        choices=["infomoney", "moneytimes", "valor", "bloomberg", "einvestidor", "all"],
        required=True,
        help="Fonte(s) para coletar (pode repetir para múltiplas)"
    )
    collect.add_argument(
        "--category",
        type=str,
        help="Categoria específica (mercados, economia, etc) - varia por fonte"
    )
    collect.add_argument(
        "--start-date",
        type=str,
        help="Data inicial para filtrar (YYYY-MM-DD) - filtra após coleta"
    )
    collect.add_argument(
        "--end-date",
        type=str,
        help="Data final para filtrar (YYYY-MM-DD) - filtra após coleta"
    )
    collect.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Máximo de artigos por fonte"
    )
    collect.add_argument(
        "--dataset-dir",
        type=Path,
        default=Path("data/processed/articles"),
        help="Diretório do dataset Parquet"
    )
    collect.add_argument(
        "--urls-out",
        type=Path,
        help="Salvar URLs coletadas em arquivo .txt (antes do scrape)"
    )
    collect.add_argument(
        "--use-proxy",
        action="store_true",
        help="Usar sistema inteligente de proxies"
    )
    collect.add_argument(
        "--proxy-fallback",
        action="store_true",
        default=True,
        help="Fallback automático de proxy (padrão: ativado)"
    )
    collect.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Browser em modo headless (padrão: ativado)"
    )
    collect.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay entre requisições (segundos)"
    )
    collect.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Apenas coletar URLs, não fazer scrape"
    )
    collect.add_argument(
        "--verbose",
        action="store_true",
        help="Modo verboso (mais logs)"
    )

    browser = sub.add_parser("browser", help="Scraping profissional com browser (JavaScript)")
    browser_sub = browser.add_subparsers(dest="browser_cmd", required=True)

    browser_yahoo = browser_sub.add_parser("yahoo-finance", help="Yahoo Finance Brasil")
    browser_yahoo.add_argument(
        "--mode",
        choices=["latest", "archive"],
        default="latest",
        help="latest: últimas notícias, archive: arquivo/categoria",
    )
    browser_yahoo.add_argument(
        "--category",
        type=str,
        default="",
        help="Categoria (para mode=archive): mercados, acoes, economia",
    )
    browser_yahoo.add_argument("--limit", type=int, default=20, help="Máximo de URLs")
    browser_yahoo.add_argument("--out", type=Path, required=True, help="Arquivo de saída (.txt)")
    browser_yahoo.add_argument(
        "--scrape",
        action="store_true",
        help="Após coletar URLs, scrape os artigos",
    )
    browser_yahoo.add_argument(
        "--dataset-dir",
        type=Path,
        help="Diretório do dataset Parquet (se --scrape)",
    )
    browser_yahoo.add_argument("--headless", action="store_true", default=True, help="Browser headless")

    browser_custom = browser_sub.add_parser("custom", help="URL customizada com seletor")
    browser_custom.add_argument("--url", type=str, required=True, help="URL para extrair")
    browser_custom.add_argument(
        "--selector",
        type=str,
        required=True,
        help="CSS selector para links (ex.: 'a.article-link')",
    )
    browser_custom.add_argument(
        "--filter",
        type=str,
        help="Filtrar URLs que contêm este texto",
    )
    browser_custom.add_argument("--out", type=Path, required=True, help="Arquivo de saída (.txt)")
    browser_custom.add_argument("--headless", action="store_true", default=True)

    browser_infomoney = browser_sub.add_parser("infomoney", help="InfoMoney (portal financeiro brasileiro)")
    browser_infomoney.add_argument(
        "--category",
        choices=["mercados", "economia", "investimentos", "negocios", "carreira"],
        default=None,
        help="Categoria específica (None = homepage com todas)",
    )
    browser_infomoney.add_argument("--limit", type=int, default=20, help="Máximo de URLs")
    browser_infomoney.add_argument("--out", type=Path, required=True, help="Arquivo de saída (.txt)")
    browser_infomoney.add_argument(
        "--scrape",
        action="store_true",
        help="Após coletar URLs, scrape os artigos",
    )
    browser_infomoney.add_argument(
        "--dataset-dir",
        type=Path,
        help="Diretório do dataset Parquet (se --scrape)",
    )
    browser_infomoney.add_argument("--headless", action="store_true", default=True)

    browser_moneytimes = browser_sub.add_parser("moneytimes", help="Money Times (notícias financeiras)")
    browser_moneytimes.add_argument("--limit", type=int, default=20, help="Máximo de URLs")
    browser_moneytimes.add_argument("--out", type=Path, required=True, help="Arquivo de saída (.txt)")
    browser_moneytimes.add_argument(
        "--scrape",
        action="store_true",
        help="Após coletar URLs, scrape os artigos",
    )
    browser_moneytimes.add_argument(
        "--dataset-dir",
        type=Path,
        help="Diretório do dataset Parquet (se --scrape)",
    )
    browser_moneytimes.add_argument("--headless", action="store_true", default=True)

    browser_valor = browser_sub.add_parser("valor", help="Valor Econômico")
    browser_valor.add_argument(
        "--category",
        choices=["financas", "empresas", "mercados", "mundo", "politica", "brasil"],
        default=None,
        help="Categoria específica"
    )
    browser_valor.add_argument("--limit", type=int, default=20, help="Máximo de URLs")
    browser_valor.add_argument("--out", type=Path, required=True, help="Arquivo de saída (.txt)")
    browser_valor.add_argument("--scrape", action="store_true", help="Scrape após coletar")
    browser_valor.add_argument("--dataset-dir", type=Path, help="Diretório Parquet")
    browser_valor.add_argument("--headless", action="store_true", default=True)

    browser_bloomberg = browser_sub.add_parser("bloomberg", help="Bloomberg Brasil")
    browser_bloomberg.add_argument(
        "--category",
        choices=["mercados", "economia", "negocios", "tecnologia"],
        default=None,
        help="Categoria específica"
    )
    browser_bloomberg.add_argument("--limit", type=int, default=20, help="Máximo de URLs")
    browser_bloomberg.add_argument("--out", type=Path, required=True, help="Arquivo de saída (.txt)")
    browser_bloomberg.add_argument("--scrape", action="store_true", help="Scrape após coletar")
    browser_bloomberg.add_argument("--dataset-dir", type=Path, help="Diretório Parquet")
    browser_bloomberg.add_argument("--headless", action="store_true", default=True)

    browser_einvestidor = browser_sub.add_parser("einvestidor", help="E-Investidor (Estadão)")
    browser_einvestidor.add_argument(
        "--category",
        choices=["mercados", "investimentos", "fundos-imobiliarios", "cripto", "acoes"],
        default=None,
        help="Categoria específica"
    )
    browser_einvestidor.add_argument("--limit", type=int, default=20, help="Máximo de URLs")
    browser_einvestidor.add_argument("--out", type=Path, required=True, help="Arquivo de saída (.txt)")
    browser_einvestidor.add_argument("--scrape", action="store_true", help="Scrape após coletar")
    browser_einvestidor.add_argument("--dataset-dir", type=Path, help="Diretório Parquet")
    browser_einvestidor.add_argument("--headless", action="store_true", default=True)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "scrape":
        urls = list(args.url)
        if args.input:
            urls.extend(_read_urls_from_file(args.input))
        if not urls:
            parser.error("Informe --url e/ou --input")
        if args.out is None and args.dataset_dir is None:
            parser.error("Informe --out e/ou --dataset-dir")

        scrape_urls(
            urls,
            args.out,
            args.format,
            dataset_dir=args.dataset_dir,
            delay_seconds=float(args.delay),
            timeout_seconds=float(args.timeout),
            respect_robots=not bool(args.no_respect_robots),
            user_agent=args.user_agent,
            max_articles=args.max,
        )
        return 0

    if args.cmd == "rss":
        links: list[str] = []
        feeds = list(args.feed)
        if args.sources_csv:
            sources = load_sources_csv(args.sources_csv)
            feeds.extend(enabled_rss_feeds(sources))

        if not feeds:
            parser.error("Informe --feed e/ou --sources-csv")

        for feed_url in feeds:
            items = collect_links_from_feed(feed_url, limit=args.limit)
            links.extend([i.url for i in items])

        if not args.scrape:
            # Se não for raspar, salva links em .txt
            if args.out is None:
                parser.error("Informe --out para salvar os links")
            _write_lines(args.out, links)
            return 0

        if args.out is None and args.dataset_dir is None:
            parser.error("Informe --out e/ou --dataset-dir")

        scrape_urls(
            links,
            args.out,
            args.format,
            dataset_dir=args.dataset_dir,
            delay_seconds=float(args.delay),
            timeout_seconds=float(args.timeout),
            respect_robots=not bool(args.no_respect_robots),
            user_agent=args.user_agent,
            max_articles=args.max,
        )
        return 0

    if args.cmd == "query":
        query_dataset(args.dataset_dir, args.sql, args.format)
        return 0

    if args.cmd == "stats":
        dataset_stats(args.dataset_dir)
        return 0
    
    if args.cmd == "collect":
        from datetime import datetime
        from .infomoney_scraper import InfoMoneyScraper
        from .moneytimes_scraper import MoneyTimesScraper
        from .valor_scraper import ValorScraper
        from .bloomberg_scraper import BloombergScraper
        from .einvestidor_scraper import EInvestidorScraper
        
        # Configurar logging se verbose
        if args.verbose:
            import logging
            logging.basicConfig(level=logging.INFO)
        
        # Determinar fontes
        sources = args.source
        if "all" in sources:
            sources = ["infomoney", "moneytimes", "valor", "bloomberg", "einvestidor"]
        else:
            sources = list(set(sources))  # Remove duplicatas
        
        print(f"🎯 Coletando de {len(sources)} fonte(s): {', '.join(sources)}")
        
        # Configurar browser
        config = BrowserConfig(
            headless=args.headless,
            use_proxy=args.use_proxy,
            proxy_fallback=args.proxy_fallback,
        )
        
        all_urls = []
        
        with ProfessionalScraper(config) as browser:
            for source_name in sources:
                print(f"\n📰 Fonte: {source_name.upper()}")
                print(f"   Limite: {args.limit} artigos")
                if args.category:
                    print(f"   Categoria: {args.category}")
                
                try:
                    urls = []
                    
                    if source_name == "infomoney":
                        scraper = InfoMoneyScraper(scraper=browser)
                        urls = scraper.get_latest_articles(
                            category=args.category,
                            limit=args.limit
                        )
                    
                    elif source_name == "moneytimes":
                        scraper = MoneyTimesScraper(scraper=browser)
                        urls = scraper.get_latest_articles(limit=args.limit)
                    
                    elif source_name == "valor":
                        scraper = ValorScraper(scraper=browser)
                        urls = scraper.get_latest_articles(
                            category=args.category,
                            limit=args.limit
                        )
                    
                    elif source_name == "bloomberg":
                        scraper = BloombergScraper(scraper=browser)
                        urls = scraper.get_latest_articles(
                            category=args.category,
                            limit=args.limit
                        )
                    
                    elif source_name == "einvestidor":
                        scraper = EInvestidorScraper(scraper=browser)
                        urls = scraper.get_latest_articles(
                            category=args.category,
                            limit=args.limit
                        )
                    
                    print(f"   ✓ Coletadas {len(urls)} URLs")
                    all_urls.extend(urls)
                    
                except Exception as e:
                    print(f"   ✗ Erro: {e}")
                    if args.verbose:
                        import traceback
                        traceback.print_exc()
        
        print(f"\n📊 Total de URLs coletadas: {len(all_urls)}")
        
        # Salvar URLs se solicitado
        if args.urls_out:
            args.urls_out.parent.mkdir(parents=True, exist_ok=True)
            args.urls_out.write_text("\n".join(all_urls) + "\n", encoding="utf-8")
            print(f"   💾 URLs salvas em: {args.urls_out}")
        
        # Scrape se não for skip
        if not args.skip_scrape:
            if not all_urls:
                print("⚠️  Nenhuma URL para scrape")
                return 1
            
            print(f"\n🔄 Iniciando scrape de {len(all_urls)} artigos...")
            print(f"   Dataset: {args.dataset_dir}")
            print(f"   Delay: {args.delay}s")
            
            scrape_urls(
                all_urls,
                out_path=None,
                dataset_dir=args.dataset_dir,
                delay_seconds=args.delay,
            )
            
            print(f"\n✅ Scrape concluído!")
            
            # Filtrar por data se especificado
            if args.start_date or args.end_date:
                print(f"\n📅 Filtrando por período...")
                
                filters = []
                if args.start_date:
                    filters.append(f"date >= '{args.start_date}'")
                    print(f"   Data inicial: {args.start_date}")
                if args.end_date:
                    filters.append(f"date <= '{args.end_date}'")
                    print(f"   Data final: {args.end_date}")
                
                where_clause = " AND ".join(filters)
                sql = f"SELECT COUNT(*) as total FROM articles WHERE {where_clause}"
                
                print(f"\n   Query: {sql}")
                query_dataset(args.dataset_dir, sql, format="table")
        
        else:
            print(f"\n⏩ Scrape pulado (--skip-scrape)")
        
        return 0

    if args.cmd == "sources":
        if args.sources_cmd == "list":
            list_sources(args.csv)
        elif args.sources_cmd == "add":
            add_source(
                args.csv,
                args.id,
                args.name,
                args.type,
                args.url,
                args.tags,
                enabled=not args.disabled,
            )
        elif args.sources_cmd == "enable":
            toggle_source(args.csv, args.id, enable=True)
        elif args.sources_cmd == "disable":
            toggle_source(args.csv, args.id, enable=False)
        return 0

    if args.cmd == "historical":
        from datetime import date

        if args.hist_cmd == "generate":
            start = date.fromisoformat(args.start)
            end = date.fromisoformat(args.end)

            if args.by_month:
                urls = generate_urls_by_month_pattern(
                    args.pattern,
                    start.year,
                    start.month,
                    end.year,
                    end.month,
                    args.out,
                )
            else:
                urls = generate_urls_by_date_pattern(args.pattern, start, end, args.out)

            print(f"Geradas {len(urls)} URLs em {args.out}")

        elif args.hist_cmd == "sitemap":
            count = save_sitemap_urls(args.url, args.out, args.filter)
            print(f"Extraídas {count} URLs do sitemap em {args.out}")

        elif args.hist_cmd == "archive":
            urls = extract_urls_from_archive_page(args.url)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text("\n".join(urls) + "\n", encoding="utf-8")
            print(f"Extraídas {len(urls)} URLs da página de arquivo em {args.out}")

        return 0

    if args.cmd == "browser":
        config = BrowserConfig(headless=args.headless)

        if args.browser_cmd == "yahoo-finance":
            print(f"Iniciando browser (headless={args.headless})...")
            with ProfessionalScraper(config) as scraper:
                yahoo = YahooFinanceScraper(scraper)

                if args.mode == "latest":
                    print(f"Coletando últimas {args.limit} notícias...")
                    urls = yahoo.get_latest_news_urls(limit=args.limit)
                else:
                    print(f"Coletando arquivo (categoria: {args.category or 'geral'})...")
                    urls = yahoo.get_archive_urls(category=args.category, limit=args.limit)

                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text("\n".join(urls) + "\n", encoding="utf-8")
                print(f"✓ {len(urls)} URLs salvas em {args.out}")

            # Scrape se solicitado
            if args.scrape:
                if not urls:
                    print("Nenhuma URL coletada para scrape.")
                    return 1

                if not args.dataset_dir:
                    parser.error("Informe --dataset-dir para scrape")

                print(f"\nIniciando scrape de {len(urls)} artigos...")
                scrape_urls(
                    urls,
                    out_path=None,
                    dataset_dir=args.dataset_dir,
                    delay_seconds=2.0,
                )
                print(f"✓ Scrape concluído: {args.dataset_dir}")

        elif args.browser_cmd == "custom":
            print(f"Iniciando browser (headless={args.headless})...")
            with ProfessionalScraper(config) as scraper:
                urls = scraper.extract_links(
                    args.url,
                    args.selector,
                    filter_contains=args.filter,
                )

                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text("\n".join(urls) + "\n", encoding="utf-8")
                print(f"✓ {len(urls)} URLs extraídas em {args.out}")

        elif args.browser_cmd == "infomoney":
            from .infomoney_scraper import InfoMoneyScraper
            
            print(f"Iniciando browser (headless={args.headless})...")
            with ProfessionalScraper(config) as scraper:
                infomoney = InfoMoneyScraper(scraper)
                
                print(f"Coletando artigos do InfoMoney (categoria: {args.category or 'todas'})...")
                urls = infomoney.get_latest_articles(
                    category=args.category,
                    limit=args.limit,
                )
                
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text("\n".join(urls) + "\n", encoding="utf-8")
                print(f"✓ {len(urls)} URLs salvas em {args.out}")
            
            # Scrape se solicitado
            if args.scrape:
                if not urls:
                    print("Nenhuma URL coletada para scrape.")
                    return 1

                if not args.dataset_dir:
                    parser.error("Informe --dataset-dir para scrape")

                print(f"\nIniciando scrape de {len(urls)} artigos...")
                scrape_urls(
                    urls,
                    out_path=None,
                    dataset_dir=args.dataset_dir,
                    delay_seconds=2.0,
                )
                print(f"✓ Scrape concluído: {args.dataset_dir}")

        elif args.browser_cmd == "moneytimes":
            from .moneytimes_scraper import MoneyTimesScraper
            
            print(f"Iniciando browser (headless={args.headless})...")
            with ProfessionalScraper(config) as scraper:
                moneytimes = MoneyTimesScraper(scraper)
                
                print(f"Coletando artigos do Money Times...")
                urls = moneytimes.get_latest_articles(limit=args.limit)
                
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text("\n".join(urls) + "\n", encoding="utf-8")
                print(f"✓ {len(urls)} URLs salvas em {args.out}")
            
            # Scrape se solicitado
            if args.scrape:
                if not urls:
                    print("Nenhuma URL coletada para scrape.")
                    return 1

                if not args.dataset_dir:
                    parser.error("Informe --dataset-dir para scrape")

                print(f"\nIniciando scrape de {len(urls)} artigos...")
                scrape_urls(
                    urls,
                    out_path=None,
                    dataset_dir=args.dataset_dir,
                    delay_seconds=2.0,
                )
                print(f"✓ Scrape concluído: {args.dataset_dir}")
        
        elif args.browser_cmd == "valor":
            from .valor_scraper import ValorScraper
            
            print(f"Iniciando browser (headless={args.headless})...")
            with ProfessionalScraper(config) as scraper:
                valor = ValorScraper(scraper)
                
                print(f"Coletando artigos do Valor (categoria: {args.category or 'todas'})...")
                urls = valor.get_latest_articles(
                    category=args.category,
                    limit=args.limit,
                )
                
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text("\n".join(urls) + "\n", encoding="utf-8")
                print(f"✓ {len(urls)} URLs salvas em {args.out}")
            
            if args.scrape:
                if not urls:
                    print("Nenhuma URL coletada para scrape.")
                    return 1
                if not args.dataset_dir:
                    parser.error("Informe --dataset-dir para scrape")
                print(f"\nIniciando scrape de {len(urls)} artigos...")
                scrape_urls(urls, out_path=None, dataset_dir=args.dataset_dir, delay_seconds=2.0)
                print(f"✓ Scrape concluído: {args.dataset_dir}")
        
        elif args.browser_cmd == "bloomberg":
            from .bloomberg_scraper import BloombergScraper
            
            print(f"Iniciando browser (headless={args.headless})...")
            with ProfessionalScraper(config) as scraper:
                bloomberg = BloombergScraper(scraper)
                
                print(f"Coletando artigos da Bloomberg (categoria: {args.category or 'todas'})...")
                urls = bloomberg.get_latest_articles(
                    category=args.category,
                    limit=args.limit,
                )
                
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text("\n".join(urls) + "\n", encoding="utf-8")
                print(f"✓ {len(urls)} URLs salvas em {args.out}")
            
            if args.scrape:
                if not urls:
                    print("Nenhuma URL coletada para scrape.")
                    return 1
                if not args.dataset_dir:
                    parser.error("Informe --dataset-dir para scrape")
                print(f"\nIniciando scrape de {len(urls)} artigos...")
                scrape_urls(urls, out_path=None, dataset_dir=args.dataset_dir, delay_seconds=2.0)
                print(f"✓ Scrape concluído: {args.dataset_dir}")
        
        elif args.browser_cmd == "einvestidor":
            from .einvestidor_scraper import EInvestidorScraper
            
            print(f"Iniciando browser (headless={args.headless})...")
            with ProfessionalScraper(config) as scraper:
                einvestidor = EInvestidorScraper(scraper)
                
                print(f"Coletando artigos do E-Investidor (categoria: {args.category or 'todas'})...")
                urls = einvestidor.get_latest_articles(
                    category=args.category,
                    limit=args.limit,
                )
                
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text("\n".join(urls) + "\n", encoding="utf-8")
                print(f"✓ {len(urls)} URLs salvas em {args.out}")
            
            if args.scrape:
                if not urls:
                    print("Nenhuma URL coletada para scrape.")
                    return 1
                if not args.dataset_dir:
                    parser.error("Informe --dataset-dir para scrape")
                print(f"\nIniciando scrape de {len(urls)} artigos...")
                scrape_urls(urls, out_path=None, dataset_dir=args.dataset_dir, delay_seconds=2.0)
                print(f"✓ Scrape concluído: {args.dataset_dir}")

        return 0

    parser.error("Comando inválido")
    return 2
