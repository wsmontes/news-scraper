from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Generator

import requests


def fetch_sitemap_urls(sitemap_url: str, filter_pattern: str | None = None) -> list[str]:
    """Extrai URLs de um sitemap XML.
    
    Args:
        sitemap_url: URL do sitemap (ex.: https://example.com/sitemap.xml)
        filter_pattern: Se fornecido, retorna apenas URLs que contêm este padrão
    
    Suporta:
    - Sitemaps simples (<urlset>)
    - Sitemap index (<sitemapindex> que aponta para outros sitemaps)
    """
    
    urls: list[str] = []
    
    try:
        resp = requests.get(sitemap_url, timeout=30)
        resp.raise_for_status()
        
        root = ET.fromstring(resp.content)
        
        # Namespace comum em sitemaps
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        
        # Sitemap index (tem <sitemap> entries)
        for sitemap in root.findall(".//sm:sitemap/sm:loc", ns):
            if sitemap.text:
                # Recursivamente busca neste sub-sitemap
                urls.extend(fetch_sitemap_urls(sitemap.text, filter_pattern))
        
        # Sitemap simples (tem <url> entries)
        for url in root.findall(".//sm:url/sm:loc", ns):
            if url.text:
                if filter_pattern is None or filter_pattern in url.text:
                    urls.append(url.text)
    
    except Exception as e:
        print(f"Erro ao buscar sitemap {sitemap_url}: {e}")
    
    return urls


def save_sitemap_urls(
    sitemap_url: str,
    output_file: Path,
    filter_pattern: str | None = None,
) -> int:
    """Extrai URLs de sitemap e salva em arquivo."""
    
    urls = fetch_sitemap_urls(sitemap_url, filter_pattern)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(urls) + "\n", encoding="utf-8")
    
    return len(urls)


def extract_urls_from_archive_page(
    archive_url: str,
    base_url: str | None = None,
) -> list[str]:
    """Extrai links de uma página de arquivo (heurística).
    
    Útil para páginas que listam artigos por data/período.
    Retorna apenas links absolutos que parecem ser artigos.
    """
    
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin, urlparse
    
    try:
        resp = requests.get(archive_url, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, "lxml")
        base = base_url or archive_url
        
        urls: list[str] = []
        
        for link in soup.find_all("a", href=True):
            href = link["href"]
            absolute_url = urljoin(base, href)
            
            # Heurística: ignora navegação comum
            parsed = urlparse(absolute_url)
            if parsed.path in {"/", ""} or parsed.path.startswith(("/categoria", "/tag", "/autor")):
                continue
            
            # Se tiver data no path, provavelmente é artigo
            if any(x in parsed.path for x in ["/20", "/arquivo", "/noticia"]):
                urls.append(absolute_url)
        
        return list(set(urls))  # deduplica
    
    except Exception as e:
        print(f"Erro ao extrair de {archive_url}: {e}")
        return []
