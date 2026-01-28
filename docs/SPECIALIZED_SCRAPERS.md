# Scrapers Especializados por Site

Este documento explica a arquitetura de scrapers especializados e como adicionar novos sites.

## Filosofia

**Não crie scrapers sem antes investigar o site.** Cada site tem estrutura única e pode requerer abordagens diferentes.

### Processo para adicionar um novo site:

1. **Investigar** - Use `scripts/investigate_site.py` para entender a estrutura
2. **Validar** - Teste extração manual de conteúdo
3. **Implementar** - Crie o módulo especializado apenas após validação
4. **Testar** - Valide com artigos reais antes de considerar pronto

## Sites Implementados

### 1. InfoMoney (`infomoney_scraper.py`)

**Status:** ✅ Testado e funcionando

**Características:**
- Portal financeiro brasileiro (www.infomoney.com.br)
- Site JavaScript-heavy (requer Selenium)
- Categorias: mercados, economia, investimentos, negocios, carreira
- URLs seguem padrão: `/categoria/titulo-slug/`
- ~15-20 artigos por página com scroll

**Uso:**
```bash
# Apenas URLs
news-scraper browser infomoney \
  --category mercados \
  --limit 20 \
  --out infomoney_urls.txt \
  --headless

# URLs + Scrape direto para Parquet
news-scraper browser infomoney \
  --category economia \
  --limit 10 \
  --out infomoney_urls.txt \
  --scrape \
  --dataset-dir data/processed/articles \
  --headless
```

**Testes realizados:**
- ✅ Extração de URLs (5 artigos testados)
- ✅ Scraping completo (3 artigos salvos em Parquet)
- ✅ Títulos completos extraídos
- ✅ Texto completo (2000-3000 chars por artigo)

### 2. Money Times (`moneytimes_scraper.py`)

**Status:** ✅ Testado e funcionando

**Características:**
- Portal financeiro brasileiro (moneytimes.com.br)
- Site acessível (não requer anti-detecção especial)
- Homepage única (sem categorias separadas)
- URLs seguem padrão: `/titulo-slug-codigo/` (ex: `-igdl/`, `-lmrs/`)
- ~78 URLs na homepage com scroll

**Uso:**
```bash
# Apenas URLs
news-scraper browser moneytimes \
  --limit 20 \
  --out moneytimes_urls.txt \
  --headless

# URLs + Scrape
news-scraper browser moneytimes \
  --limit 10 \
  --out moneytimes_urls.txt \
  --scrape \
  --dataset-dir data/processed/articles \
  --headless
```

**Testes realizados:**
- ✅ Extração de URLs (78 encontradas, 5 testadas)
- ⏳ Scraping completo (pendente teste)

### 3. Yahoo Finance Brasil (`yahoo_finance.py`)

**Status:** ❌ Bloqueado

**Problema:** 
- Yahoo redireciona para Yahoo Search (detecção de bot)
- Anti-detecção atual não suficiente
- Requer cookies/sessão mais complexos

**Não usar até resolver o problema de bloqueio.**

## Como Adicionar um Novo Site

### 1. Investigação

Use o script de investigação:

```bash
python scripts/investigate_site.py https://exemplo.com.br/
```

Isso vai:
- Carregar a página com Selenium
- Fazer scroll para conteúdo dinâmico
- Listar URLs de possíveis artigos
- Testar extração de conteúdo em um artigo

### 2. Análise Manual

Abra o site no navegador e responda:

**Estrutura de URLs:**
- [ ] URLs têm data? (ex: `/2025/01/27/titulo/`)
- [ ] URLs têm categoria? (ex: `/economia/titulo/`)
- [ ] URLs têm código/slug? (ex: `-abc123/`)
- [ ] Qual o padrão geral?

**Navegação:**
- [ ] Homepage mostra artigos recentes?
- [ ] Tem seção de arquivo/categorias?
- [ ] Usa lazy-load/scroll infinito?
- [ ] Quantos artigos por página?

**Conteúdo:**
- [ ] Trafilatura extrai bem o texto?
- [ ] Título está em meta tags ou tags HTML?
- [ ] Data de publicação é extraída?
- [ ] Autor é extraído?

### 3. Implementação

Crie `src/news_scraper/<site>_scraper.py`:

```python
"""
Scraper especializado para <Site> (<url>).

Descrição do site.
Estrutura testada e validada em <data>.

Características:
- Característica 1
- Característica 2
- etc.
"""

from __future__ import annotations
from news_scraper.browser import ProfessionalScraper


class <Site>Scraper:
    """Scraper especializado para <Site>."""
    
    def __init__(self, scraper: ProfessionalScraper):
        self.scraper = scraper
        self.base_url = "https://exemplo.com"
    
    def get_latest_articles(self, limit: int = 20) -> list[str]:
        """
        Extrai URLs dos artigos mais recentes.
        
        Args:
            limit: Número máximo de URLs
            
        Returns:
            Lista de URLs de artigos
        """
        print(f"Coletando de: {self.base_url}")
        
        # 1. Carregar página
        self.scraper.get_page(self.base_url, wait_time=3)
        
        # 2. Scroll se necessário
        self.scraper.scroll_and_load(scroll_pause=1.5, max_scrolls=3)
        
        # 3. Extrair links
        all_links = self.scraper.driver.find_elements('css selector', 'a')
        
        article_urls: set[str] = set()
        
        for link in all_links:
            href = link.get_attribute('href')
            
            # Aplicar filtros específicos do site
            if self._is_article_url(href):
                article_urls.add(href)
        
        sorted_urls = sorted(article_urls)[:limit]
        print(f"✓ {len(sorted_urls)} URLs encontradas")
        
        return sorted_urls
    
    def _is_article_url(self, url: str | None) -> bool:
        """Verifica se URL é de um artigo."""
        if not url or 'exemplo.com' not in url:
            return False
        
        # Aplicar lógica específica do site
        # Exemplos:
        # - Tamanho mínimo da URL
        # - Padrão de categoria/data
        # - Excluir páginas de navegação
        
        return True


def scrape_<site>(limit: int = 20, headless: bool = True) -> list[str]:
    """Função de conveniência para scraping."""
    from news_scraper.browser import BrowserConfig, ProfessionalScraper
    
    config = BrowserConfig(headless=headless)
    
    with ProfessionalScraper(config) as scraper:
        site_scraper = <Site>Scraper(scraper)
        return site_scraper.get_latest_articles(limit=limit)
```

### 4. Integração com CLI

Adicione ao `cli.py`:

**No parser (função `build_parser()`):**
```python
browser_<site> = browser_sub.add_parser("<site>", help="Descrição")
browser_<site>.add_argument("--limit", type=int, default=20)
browser_<site>.add_argument("--out", type=Path, required=True)
browser_<site>.add_argument("--scrape", action="store_true")
browser_<site>.add_argument("--dataset-dir", type=Path)
browser_<site>.add_argument("--headless", action="store_true", default=True)
```

**No handler (função `main()`):**
```python
elif args.browser_cmd == "<site>":
    from .<site>_scraper import <Site>Scraper
    
    print(f"Iniciando browser (headless={args.headless})...")
    with ProfessionalScraper(config) as scraper:
        site = <Site>Scraper(scraper)
        urls = site.get_latest_articles(limit=args.limit)
        
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text("\n".join(urls) + "\n", encoding="utf-8")
        print(f"✓ {len(urls)} URLs salvas em {args.out}")
    
    if args.scrape:
        # ... código de scraping padrão
```

### 5. Teste

```bash
# Reinstalar
pip install -e . --no-deps --force-reinstall -q

# Testar extração
news-scraper browser <site> --limit 5 --out test_urls.txt --headless

# Verificar URLs
cat test_urls.txt

# Testar scraping completo
news-scraper browser <site> \
  --limit 3 \
  --out test_urls.txt \
  --scrape \
  --dataset-dir data/test \
  --headless

# Verificar dados
news-scraper stats --dataset-dir data/test
news-scraper query --dataset-dir data/test \
  --sql "SELECT title, LENGTH(text) FROM articles"
```

### 6. Documentação

Adicione ao final deste arquivo:

```markdown
### N. <Site Name> (`<site>_scraper.py`)

**Status:** ✅/⏳/❌

**Características:**
- Descrição
- URLs pattern
- Quantidade de artigos

**Uso:**
\```bash
news-scraper browser <site> --limit 20 --out urls.txt
\```

**Testes realizados:**
- ✅/❌ Item 1
- ✅/❌ Item 2
```

## Padrões de Projeto

### Filtragem de URLs

Sempre excluir páginas de navegação:
```python
excluded_patterns = [
    '/autor/', '/tag/', '/categoria/', '/page/',
    '/busca/', '/search/', '/sobre/', '/contato/',
    'utm_', 'facebook', 'twitter', 'linkedin',
    'newsletter', 'cadastro', 'login'
]

if not any(pattern in url.lower() for pattern in excluded_patterns):
    article_urls.add(url)
```

### Scroll Inteligente

Ajustar parâmetros por site:
```python
# Site lento/pesado
self.scraper.scroll_and_load(scroll_pause=2.0, max_scrolls=5)

# Site rápido
self.scraper.scroll_and_load(scroll_pause=1.0, max_scrolls=2)
```

### Limite com Margem

Coletar extras e filtrar depois:
```python
if len(article_urls) >= limit * 2:  # 2x margem de segurança
    break

sorted_urls = sorted(article_urls)[:limit]  # Pegar apenas o necessário
```

## Troubleshooting

### "0 URLs encontradas"

1. Verifique os filtros (tamanho mínimo, padrões excluídos)
2. Inspecione HTML manualmente (navegador dev tools)
3. Teste sem headless para ver o que o browser carrega
4. Aumente tempo de espera (`wait_time`)

### "Texto não extraído"

1. Teste URL individual com `requests + extract_article`
2. Verifique se site requer JavaScript (use browser)
3. Considere seletores CSS específicos se trafilatura falhar

### "Site bloqueia/redireciona"

1. Adicione delays maiores
2. Rotacione user agents
3. Use proxies se necessário
4. Alguns sites são intransponíveis - documente e pule

## Próximos Sites Candidatos

Sites brasileiros de notícias financeiras para investigar:

- [ ] **Exame** (exame.com) - Portal de negócios
- [ ] **Valor Econômico** (valor.globo.com) - Jornal financeiro
- [ ] **Start SE** (startse.com) - Inovação e startups
- [ ] **Brazil Journal** (braziljournal.com) - Notícias de negócios
- [ ] **G1 Economia** (g1.globo.com/economia) - Portal de notícias

**Lembre-se:** Investigar ANTES de implementar!
