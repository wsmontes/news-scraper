from __future__ import annotations

import sys
from pathlib import Path

import duckdb


def query_dataset(dataset_dir: Path, sql: str, output_format: str = "table") -> None:
    """Executa query SQL no dataset Parquet usando DuckDB.
    
    O dataset é exposto como 'articles' na query.
    """
    
    if not dataset_dir.exists():
        print(f"Dataset não encontrado: {dataset_dir}", file=sys.stderr)
        sys.exit(1)
    
    pattern = str(dataset_dir / "**" / "*.parquet")
    
    con = duckdb.connect()
    
    # Registra o dataset como uma tabela virtual
    con.execute(f"CREATE VIEW articles AS SELECT * FROM read_parquet('{pattern}')")
    
    try:
        result = con.execute(sql).fetchall()
        columns = [desc[0] for desc in con.description] if con.description else []
        
        if output_format == "csv":
            # CSV simples
            if columns:
                print(",".join(columns))
            for row in result:
                print(",".join(str(v) if v is not None else "" for v in row))
        elif output_format == "json":
            # JSON lines
            import json
            for row in result:
                obj = dict(zip(columns, row))
                print(json.dumps(obj, ensure_ascii=False, default=str))
        else:
            # Table format (padrão)
            if columns:
                # Header
                col_widths = [max(len(str(col)), 12) for col in columns]
                header = " | ".join(str(col).ljust(w) for col, w in zip(columns, col_widths))
                print(header)
                print("-" * len(header))
                
                # Rows
                for row in result:
                    print(" | ".join(str(v).ljust(w) if v is not None else "".ljust(w) for v, w in zip(row, col_widths)))
            
            print(f"\n({len(result)} rows)")
    
    except Exception as e:
        print(f"Erro na query: {e}", file=sys.stderr)
        sys.exit(1)


def dataset_stats(dataset_dir: Path) -> None:
    """Mostra estatísticas do dataset."""
    
    if not dataset_dir.exists():
        print(f"Dataset não encontrado: {dataset_dir}", file=sys.stderr)
        sys.exit(1)
    
    pattern = str(dataset_dir / "**" / "*.parquet")
    con = duckdb.connect()
    
    # Total
    total = con.execute(f"SELECT count(*) FROM read_parquet('{pattern}')").fetchone()[0]
    print(f"Total de artigos: {total}")
    
    if total == 0:
        return
    
    # Por fonte
    print("\nArtigos por fonte:")
    sources = con.execute(
        f"SELECT source, count(*) as cnt FROM read_parquet('{pattern}') GROUP BY source ORDER BY cnt DESC LIMIT 10"
    ).fetchall()
    for source, cnt in sources:
        print(f"  {source}: {cnt}")
    
    # Range de datas
    print("\nPeríodo:")
    dates = con.execute(
        f"""
        SELECT 
            min(date_published) as primeiro, 
            max(date_published) as ultimo
        FROM read_parquet('{pattern}')
        WHERE date_published IS NOT NULL
        """
    ).fetchone()
    if dates and dates[0]:
        print(f"  Primeiro: {dates[0]}")
        print(f"  Último: {dates[1]}")
    
    # Com erro
    errors = con.execute(
        f"SELECT count(*) FROM read_parquet('{pattern}') WHERE error IS NOT NULL"
    ).fetchone()[0]
    if errors > 0:
        print(f"\nArtigos com erro: {errors}")
