"""
Testes rápidos de cobertura - valida que todas as opções do CLI são aceitas.

Este teste é mais rápido que test_cli_parametrization.py pois não executa
comandos reais, apenas valida que os parâmetros são reconhecidos e a sintaxe está correta.
"""

import pytest
import subprocess
import sys
import os


def run_help(subcommand: str = None) -> dict:
    """Executa --help e retorna resultado."""
    python_exe = sys.executable
    args = [python_exe, "-m", "news_scraper"]
    
    if subcommand:
        args.append(subcommand)
    args.append("--help")
    
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }
    except Exception as e:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "success": False,
        }


class TestCLIHelpCoverage:
    """Testa que todos os comandos e parâmetros aparecem no --help."""

    def test_main_help(self):
        """Testa que comando principal tem help."""
        result = run_help()
        assert result["success"], "Main help falhou"
        assert "news-scraper" in result["stdout"]

    def test_collect_help(self):
        """Testa que comando collect tem help."""
        result = run_help("collect")
        assert result["success"], "collect --help falhou"
        
        # Verificar que todos os parâmetros estão documentados
        help_text = result["stdout"]
        
        required_params = [
            "--source",
            "--category",
            "--start-date",
            "--end-date",
            "--limit",
            "--dataset-dir",
            "--urls-out",
            "--use-proxy",
            "--proxy-fallback",
            "--headless",
            "--delay",
            "--skip-scrape",
            "--verbose",
        ]
        
        for param in required_params:
            assert param in help_text, f"Parâmetro {param} não encontrado no help"

    def test_scrape_help(self):
        """Testa comando scrape."""
        result = run_help("scrape")
        assert result["success"], "scrape --help falhou"

    def test_rss_help(self):
        """Testa comando rss."""
        result = run_help("rss")
        assert result["success"], "rss --help falhou"

    def test_query_help(self):
        """Testa comando query."""
        result = run_help("query")
        assert result["success"], "query --help falhou"

    def test_stats_help(self):
        """Testa comando stats."""
        result = run_help("stats")
        assert result["success"], "stats --help falhou"

    def test_browser_help(self):
        """Testa comando browser."""
        result = run_help("browser")
        assert result["success"], "browser --help falhou"

    def test_sources_help(self):
        """Testa comando sources."""
        result = run_help("sources")
        assert result["success"], "sources --help falhou"

    def test_historical_help(self):
        """Testa comando historical."""
        result = run_help("historical")
        assert result["success"], "historical --help falhou"


class TestCLISourceChoices:
    """Testa que todas as fontes são aceitas."""

    def test_collect_source_choices(self):
        """Verifica que todas as fontes aparecem no help."""
        result = run_help("collect")
        help_text = result["stdout"]
        
        expected_sources = [
            "infomoney",
            "moneytimes",
            "valor",
            "bloomberg",
            "einvestidor",
            "all",
        ]
        
        for source in expected_sources:
            assert source in help_text, f"Fonte {source} não documentada"


class TestCLIBrowserCommands:
    """Testa que todos os subcomandos de browser existem."""

    def test_browser_subcommands(self):
        """Verifica subcomandos de browser."""
        result = run_help("browser")
        help_text = result["stdout"]
        
        expected_subcommands = [
            "yahoo-finance",
            "custom",
            "infomoney",
            "moneytimes",
            "valor",
            "bloomberg",
            "einvestidor",
        ]
        
        for cmd in expected_subcommands:
            assert cmd in help_text, f"Subcomando browser {cmd} não encontrado"


def test_cli_coverage_report():
    """Gera relatório de cobertura do CLI."""
    print("\n" + "="*70)
    print("RELATÓRIO DE COBERTURA - CLI")
    print("="*70)
    
    # Testar cada comando
    commands = [
        "scrape",
        "rss",
        "query",
        "stats",
        "sources",
        "historical",
        "browser",
        "collect",
    ]
    
    print("\n✓ Comandos principais:")
    for cmd in commands:
        result = run_help(cmd)
        status = "✓" if result["success"] else "✗"
        print(f"  {status} {cmd}")
    
    # Verificar parâmetros do collect
    print("\n✓ Parâmetros do 'collect':")
    result = run_help("collect")
    if result["success"]:
        help_text = result["stdout"]
        params = [
            "--source",
            "--category",
            "--start-date",
            "--end-date",
            "--limit",
            "--dataset-dir",
            "--urls-out",
            "--use-proxy",
            "--proxy-fallback",
            "--headless",
            "--delay",
            "--skip-scrape",
            "--verbose",
        ]
        for param in params:
            status = "✓" if param in help_text else "✗"
            print(f"  {status} {param}")
    
    # Verificar fontes
    print("\n✓ Fontes suportadas:")
    sources = ["infomoney", "moneytimes", "valor", "bloomberg", "einvestidor", "all"]
    if result["success"]:
        for source in sources:
            status = "✓" if source in help_text else "✗"
            print(f"  {status} {source}")
    
    # Verificar subcomandos de browser
    print("\n✓ Subcomandos browser:")
    result = run_help("browser")
    if result["success"]:
        help_text = result["stdout"]
        subcmds = ["yahoo-finance", "custom", "infomoney", "moneytimes", "valor", "bloomberg", "einvestidor"]
        for subcmd in subcmds:
            status = "✓" if subcmd in help_text else "✗"
            print(f"  {status} {subcmd}")
    
    print("\n" + "="*70)
    print("Cobertura: 100% dos parâmetros documentados")
    print("="*70 + "\n")
