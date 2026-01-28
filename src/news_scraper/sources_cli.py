from __future__ import annotations

import csv
import sys
from pathlib import Path

from .sources import Source, load_sources_csv


def list_sources(csv_path: Path) -> None:
    """Lista fontes do CSV."""
    
    if not csv_path.exists():
        print(f"Arquivo não encontrado: {csv_path}", file=sys.stderr)
        sys.exit(1)
    
    sources = load_sources_csv(csv_path)
    
    if not sources:
        print("Nenhuma fonte configurada.")
        return
    
    # Header
    print(f"{'ID':<20} {'Nome':<30} {'Tipo':<8} {'Enabled':<8} {'URL':<50}")
    print("-" * 120)
    
    for src in sources:
        enabled = "✓" if src.enabled else "✗"
        url_truncated = src.url if len(src.url) <= 50 else src.url[:47] + "..."
        print(f"{src.source_id:<20} {src.name:<30} {src.type:<8} {enabled:<8} {url_truncated:<50}")
    
    print(f"\nTotal: {len(sources)} ({sum(1 for s in sources if s.enabled)} habilitadas)")


def add_source(
    csv_path: Path,
    source_id: str,
    name: str,
    type_: str,
    url: str,
    tags: str | None = None,
    enabled: bool = True,
) -> None:
    """Adiciona uma fonte ao CSV."""
    
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Carrega existentes para evitar duplicar
    existing_ids = set()
    if csv_path.exists():
        sources = load_sources_csv(csv_path)
        existing_ids = {s.source_id for s in sources}
    
    if source_id in existing_ids:
        print(f"Fonte '{source_id}' já existe. Use outro ID.", file=sys.stderr)
        sys.exit(1)
    
    # Append
    with csv_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        
        # Se arquivo vazio, escreve header
        if csv_path.stat().st_size == 0:
            writer.writerow(["enabled", "source_id", "name", "type", "url", "tags"])
        
        writer.writerow([
            "1" if enabled else "0",
            source_id,
            name,
            type_,
            url,
            tags or "",
        ])
    
    print(f"Fonte '{source_id}' adicionada com sucesso.")


def toggle_source(csv_path: Path, source_id: str, enable: bool) -> None:
    """Habilita/desabilita uma fonte no CSV."""
    
    if not csv_path.exists():
        print(f"Arquivo não encontrado: {csv_path}", file=sys.stderr)
        sys.exit(1)
    
    sources = load_sources_csv(csv_path)
    found = False
    
    for src in sources:
        if src.source_id == source_id:
            src.enabled = enable
            found = True
            break
    
    if not found:
        print(f"Fonte '{source_id}' não encontrada.", file=sys.stderr)
        sys.exit(1)
    
    # Reescreve o CSV
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["enabled", "source_id", "name", "type", "url", "tags"])
        
        for src in sources:
            writer.writerow([
                "1" if src.enabled else "0",
                src.source_id,
                src.name,
                src.type,
                src.url,
                ";".join(src.tags),
            ])
    
    action = "habilitada" if enable else "desabilitada"
    print(f"Fonte '{source_id}' {action} com sucesso.")
