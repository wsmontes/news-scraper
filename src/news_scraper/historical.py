from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path


def generate_urls_by_date_pattern(
    pattern: str,
    start_date: date,
    end_date: date,
    output_file: Path | None = None,
) -> list[str]:
    """Gera URLs baseadas em padrão de data.
    
    Placeholders suportados:
    - {YYYY} - ano (4 dígitos)
    - {YY} - ano (2 dígitos)
    - {MM} - mês (01-12)
    - {M} - mês sem zero (1-12)
    - {DD} - dia (01-31)
    - {D} - dia sem zero (1-31)
    
    Exemplo:
        pattern = "https://example.com/arquivo/{YYYY}/{MM}/{DD}/"
        start_date = date(2020, 1, 1)
        end_date = date(2020, 1, 31)
        
    Gera:
        https://example.com/arquivo/2020/01/01/
        https://example.com/arquivo/2020/01/02/
        ...
        https://example.com/arquivo/2020/01/31/
    """
    
    urls: list[str] = []
    current = start_date
    
    while current <= end_date:
        url = pattern
        url = url.replace("{YYYY}", f"{current.year:04d}")
        url = url.replace("{YY}", f"{current.year % 100:02d}")
        url = url.replace("{MM}", f"{current.month:02d}")
        url = url.replace("{M}", str(current.month))
        url = url.replace("{DD}", f"{current.day:02d}")
        url = url.replace("{D}", str(current.day))
        
        urls.append(url)
        current += timedelta(days=1)
    
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("\n".join(urls) + "\n", encoding="utf-8")
    
    return urls


def generate_urls_by_month_pattern(
    pattern: str,
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int,
    output_file: Path | None = None,
) -> list[str]:
    """Gera URLs baseadas em padrão de ano/mês.
    
    Útil para sites que organizam por mês (ex.: páginas de arquivo).
    
    Exemplo:
        pattern = "https://example.com/arquivo/{YYYY}/{MM}/"
        start_year, start_month = 2020, 1
        end_year, end_month = 2020, 12
    """
    
    urls: list[str] = []
    
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        url = pattern
        url = url.replace("{YYYY}", f"{year:04d}")
        url = url.replace("{YY}", f"{year % 100:02d}")
        url = url.replace("{MM}", f"{month:02d}")
        url = url.replace("{M}", str(month))
        
        urls.append(url)
        
        # Próximo mês
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("\n".join(urls) + "\n", encoding="utf-8")
    
    return urls


def extract_date_from_url(url: str) -> date | None:
    """Tenta extrair data de uma URL.
    
    Procura padrões comuns:
    - /2020/01/15/
    - /20200115/
    - ?date=2020-01-15
    """
    
    # Padrão: /YYYY/MM/DD/
    match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
    if match:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    
    # Padrão: /YYYYMMDD/
    match = re.search(r'/(\d{4})(\d{2})(\d{2})/', url)
    if match:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    
    # Padrão: ?date=YYYY-MM-DD
    match = re.search(r'[?&]date=(\d{4})-(\d{2})-(\d{2})', url)
    if match:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    
    return None
