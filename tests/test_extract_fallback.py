from __future__ import annotations

from news_scraper.extract import extract_article


def test_extract_article_fallback_parses_title_and_text():
    html = """
    <html>
      <head><title>Minha Notícia</title></head>
      <body><p>Primeiro parágrafo.</p><p>Segundo parágrafo.</p></body>
    </html>
    """
    article = extract_article(html, "https://example.com/a")
    assert article.title
    assert "Minha Notícia" in article.title
    assert article.text
    assert "Primeiro" in article.text
