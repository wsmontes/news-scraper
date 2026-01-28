# Scrapers Especializados para Fontes de Notícias Financeiras

Este documento descreve os scrapers especializados para as 5 principais fontes de notícias financeiras do Brasil.

## 📰 Fontes Suportadas

### 1. InfoMoney (`infomoney_scraper.py`)
- **URL**: https://www.infomoney.com.br
- **Categorias**: mercados, economia, investimentos, negocios, carreira
- **Características**: Site JavaScript-heavy, URLs longas com categorias
- **Teste**: `test_infomoney_scraper.py`

### 2. Valor Econômico (`valor_scraper.py`)
- **URL**: https://valor.globo.com
- **Categorias**: financas, empresas, mercados, mundo, politica, brasil
- **Características**: Data inclusa na URL (formato: /ano/mes/dia/)
- **Teste**: `test_valor_scraper.py`

### 3. Bloomberg Brasil (`bloomberg_scraper.py`)
- **URL**: https://www.bloomberg.com.br
- **Categorias**: mercados, economia, politica, empresas
- **Características**: Arquitetura internacional Bloomberg
- **Teste**: `test_bloomberg_scraper.py`

### 4. E-Investidor/Estadão (`einvestidor_scraper.py`)
- **URL**: https://einvestidor.estadao.com.br
- **Categorias**: investimentos, mercados, colunas, acoes, fundos-imobiliarios
- **Características**: Foco em educação financeira
- **Teste**: `test_einvestidor_scraper.py`

### 5. Money Times (`moneytimes_scraper.py`)
- **URL**: https://www.moneytimes.com.br
- **Categorias**: Homepage principal
- **Características**: URLs com códigos únicos
- **Teste**: `test_moneytimes_scraper.py`

## 🚀 Uso Rápido

### Exemplo Individual

```python
from news_scraper.infomoney_scraper import scrape_infomoney

# Coletar URLs de artigos
urls = scrape_infomoney(category='mercados', limit=10, headless=True)
print(f"Coletadas {len(urls)} URLs")
```

### Exemplo com Extração Completa

```python
from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper.valor_scraper import ValorScraper
from news_scraper.extract import extract_article_metadata

config = BrowserConfig(headless=True)

with ProfessionalScraper(config) as scraper:
    valor = ValorScraper(scraper)
    
    # Coletar URLs
    urls = valor.get_financas_articles(limit=5)
    
    # Extrair metadados de cada artigo
    for url in urls:
        scraper.get_page(url, wait_time=3)
        article = extract_article_metadata(url, scraper.driver)
        
        print(f"Título: {article.title}")
        print(f"Data: {article.date_published}")
        print(f"Autor: {article.author}")
        print(f"Texto: {len(article.text)} caracteres")
```

### Exemplo Multi-Fonte

```python
from news_scraper.browser import BrowserConfig, ProfessionalScraper
from news_scraper import (
    InfoMoneyScraper,
    ValorScraper,
    BloombergScraper,
    EInvestidorScraper,
    MoneyTimesScraper,
)

config = BrowserConfig(headless=True)

with ProfessionalScraper(config) as scraper:
    # InfoMoney
    infomoney = InfoMoneyScraper(scraper)
    urls_im = infomoney.get_mercados_articles(limit=5)
    
    # Valor
    valor = ValorScraper(scraper)
    urls_valor = valor.get_financas_articles(limit=5)
    
    # Bloomberg
    bloomberg = BloombergScraper(scraper)
    urls_bb = bloomberg.get_mercados_articles(limit=5)
    
    # E-Investidor
    einvestidor = EInvestidorScraper(scraper)
    urls_ei = einvestidor.get_investimentos_articles(limit=5)
    
    # Money Times
    moneytimes = MoneyTimesScraper(scraper)
    urls_mt = moneytimes.get_latest_articles(limit=5)
    
    # Consolidar
    all_urls = urls_im + urls_valor + urls_bb + urls_ei + urls_mt
    print(f"Total: {len(all_urls)} URLs coletadas")
```

## 🧪 Testes

Todos os scrapers possuem testes que validam:

1. ✅ **Coleta de URLs**: Verifica se as URLs são coletadas corretamente
2. ✅ **Filtros de Categoria**: Valida se os filtros funcionam
3. ✅ **Extração de Metadados**: Garante que todos os campos essenciais são extraídos
4. ✅ **Taxa de Sucesso**: Verifica se pelo menos 80% dos artigos têm metadados completos

### Executar Testes

```bash
# Todos os testes de scrapers
pytest tests/test_*_scraper.py -v

# Teste específico
pytest tests/test_infomoney_scraper.py -v

# Com output detalhado
pytest tests/test_valor_scraper.py -v -s
```

## 📊 Metadados Garantidos

Cada scraper garante a extração dos seguintes campos:

- **url**: URL completa do artigo
- **title**: Título completo da notícia
- **date_published**: Data de publicação (datetime)
- **author**: Autor(es) quando disponível
- **text**: Texto completo do artigo
- **source**: Nome da fonte
- **scraped_at**: Data/hora da coleta
- **language**: Idioma do conteúdo
- **extra**: Metadados adicionais específicos

### Importância da Data

**A data de publicação é crítica** para análises financeiras. Todos os scrapers foram projetados para:

1. Extrair datas confiáveis dos metadados HTML
2. Validar formatos de data
3. Fallback para data na URL quando disponível (ex: Valor)
4. Garantir timezone correto (America/Sao_Paulo)

## 🎯 Demonstração

Execute o script de demonstração para ver todos os scrapers em ação:

```bash
python -m scripts.demo_all_sources
```

Este script:
- Coleta URLs de cada fonte
- Extrai metadados completos
- Valida todos os campos
- Mostra estatísticas de sucesso

## 🛠️ Configuração

### Parâmetros Comuns

Todos os scrapers aceitam:

- **category**: Categoria específica ou None para homepage
- **limit**: Número máximo de URLs (padrão: 20)
- **headless**: Executar browser invisível (padrão: True)

### Customização

```python
from news_scraper.browser import BrowserConfig

# Configuração customizada
config = BrowserConfig(
    headless=True,
    user_agent="seu-user-agent",
    window_size=(1920, 1080)
)
```

## ⚠️ Considerações

1. **Rate Limiting**: Respeite os limites de cada site
2. **Robots.txt**: Verifique permissões antes de fazer scraping em massa
3. **Termos de Uso**: Consulte os termos de serviço de cada portal
4. **Performance**: Sites JavaScript-heavy podem ser lentos
5. **Manutenção**: Estruturas HTML podem mudar com atualizações

## 📈 Performance

Tempos médios (headless, 3 artigos):

- InfoMoney: ~15s
- Valor: ~20s
- Bloomberg: ~18s
- E-Investidor: ~12s
- Money Times: ~10s

## 🔄 Atualizações

Para manter os scrapers funcionando:

1. Execute os testes regularmente
2. Monitore mudanças nas estruturas HTML
3. Ajuste seletores CSS/XPath conforme necessário
4. Atualize testes quando necessário

## 📝 Licença

Veja LICENSE no repositório principal.
