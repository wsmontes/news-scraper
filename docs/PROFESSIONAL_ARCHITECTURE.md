# Arquitetura Profissional de Scraping

## Visão Geral

Sistema modular de scraping com múltiplas estratégias de extração, fallbacks automáticos e ferramentas profissionais de nível empresarial.

## Módulos Principais

### 1. `extractors.py` - Estratégias de Extração

**Múltiplos Extratores com Fallback Automático:**

#### Extratores Disponíveis:

1. **CustomSelectorExtractor**
   - Seletores CSS específicos por domínio
   - Maior precisão para sites conhecidos
   - Configurável via dicionário de seletores
   - Exemplo:
   ```python
   selectors = {
       "infomoney.com.br": {
           "title": "h1.article-title",
           "text": "div.article-body p",
           "date": "time.published",
           "author": "span.author-name"
       }
   }
   ```

2. **TrafilaturaExtractor**
   - Extração robusta de conteúdo principal
   - Remoção automática de boilerplate
   - Suporta múltiplos formatos de saída
   - Boa performance

3. **Newspaper3kExtractor**
   - Especializado em artigos de notícias
   - Extração de metadados rica (NLP)
   - Detecção de idioma
   - Keywords automáticas

4. **ReadabilityExtractor**
   - Algoritmo de legibilidade do Mozilla
   - Foco no conteúdo principal
   - Remove distrações

5. **BeautifulSoupExtractor**
   - Fallback universal
   - Heurísticas genéricas
   - Funciona com qualquer HTML
   - Sempre disponível

#### ExtractionPipeline

Sistema que coordena múltiplos extratores:

```python
from news_scraper.extractors import ExtractionPipeline

pipeline = ExtractionPipeline()
result = pipeline.extract(html, url, min_quality=0.3)

# Métricas automáticas:
# - result.confidence: 0.0 a 1.0
# - result.quality_score(): Score de qualidade
# - result.extractor: Nome do extrator usado
```

**Funcionamento:**
1. Tenta cada extrator na ordem de prioridade
2. Calcula score de qualidade para cada resultado
3. Retorna o melhor resultado acima do threshold
4. Se conseguir score >= 0.8, para imediatamente

**Quality Score (0.0 a 1.0):**
- Title: 30%
- Text (500+ chars): 40%
- Date: 10%
- Authors: 10%
- Description: 5%
- Image: 5%

### 2. `tools.py` - Ferramentas Profissionais

#### UserAgentRotator
Rotação de user agents realistas:
```python
from news_scraper.tools import UserAgentRotator

rotator = UserAgentRotator()
headers = rotator.get_browser_headers(url)
# Retorna headers completos simulando navegador real
```

**User Agents:** Chrome, Firefox, Safari, Edge (Windows/Mac)

#### RateLimiter & DomainRateLimiter
Rate limiting inteligente por domínio:
```python
from news_scraper.tools import DomainRateLimiter

limiter = DomainRateLimiter(default_delay=2.0)
limiter.set_domain_delay("valor.globo.com", 5.0)  # Mais cauteloso
limiter.wait(domain)  # Espera automática
```

#### RetryStrategy
Retry com backoff exponencial e jitter:
```python
from news_scraper.tools import RetryStrategy, RetryConfig

config = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True
)

strategy = RetryStrategy(config)
result = strategy.execute(fetch_function, url)
```

#### SimpleCache
Cache em disco com TTL:
```python
from news_scraper.tools import SimpleCache
from pathlib import Path

cache = SimpleCache(Path("data/cache"), ttl_hours=24)
cached_value = cache.get(url)
if not cached_value:
    value = expensive_operation()
    cache.set(url, value)
```

#### PaywallDetector
Detecta paywalls e conteúdo bloqueado:
```python
from news_scraper.tools import PaywallDetector

detector = PaywallDetector()
info = detector.detect(html, text)

# info = {
#     "has_paywall": bool,
#     "confidence": 0.0-1.0,
#     "indicators": ["text:assine", "selector:.paywall", ...]
# }
```

**Indicadores:**
- Palavras-chave: "assine", "assinante", "conteúdo exclusivo"
- Seletores CSS: `.paywall`, `.subscription-required`
- Texto muito curto (< 200 chars)

#### TextCleaner
Limpeza avançada de texto:
```python
from news_scraper.tools import TextCleaner

cleaner = TextCleaner()
clean_text = cleaner.clean(raw_text)
no_boilerplate = cleaner.remove_boilerplate(text)
paragraphs = cleaner.extract_paragraphs(text, min_length=50)
```

**Remove:**
- Múltiplas quebras de linha
- Espaços excessivos
- Copyright e rodapés
- Links de compartilhamento
- Calls to action de newsletter

#### DateNormalizer
Normaliza datas para ISO:
```python
from news_scraper.tools import DateNormalizer

normalizer = DateNormalizer()
iso_date = normalizer.normalize("28 de janeiro de 2026")
# Retorna: "2026-01-28"
```

**Suporta:**
- ISO: `2026-01-28`, `2026-01-28T14:30:00`
- Brasileiro: `28/01/2026`
- Por extenso: `28 de janeiro de 2026`
- Timestamps

#### ContentValidator
Valida qualidade do conteúdo:
```python
from news_scraper.tools import ContentValidator

validator = ContentValidator()
valid_title = validator.validate_title(title)
valid_text = validator.validate_text(text, min_length=100)
is_article = validator.is_article_content(text)
```

**Validações:**
- Tamanho mínimo
- Presença de caracteres alfabéticos
- Densidade de palavras
- Pontuação de frases
- Não é lista de links

#### LanguageDetector
Detecta idioma do texto:
```python
from news_scraper.tools import LanguageDetector

detector = LanguageDetector()
lang = detector.detect(text)  # 'pt', 'en', etc.
is_pt = detector.is_portuguese(text)
```

#### AntiBotEvasion
Técnicas anti-detecção:
```python
from news_scraper.tools import AntiBotEvasion

AntiBotEvasion.random_delay(1.0, 3.0)
headers = AntiBotEvasion.get_realistic_headers(referer=previous_url)
needs_cookies = AntiBotEvasion.should_add_cookies(domain)
```

### 3. `extract.py` - Integração

Orquestração de todos os métodos:

```python
from news_scraper.extract import extract_article

article = extract_article(html, url)
# Tenta automaticamente:
# 1. ExtractionPipeline (múltiplos extratores)
# 2. Trafilatura (fallback)
# 3. BeautifulSoup (fallback final)
```

**Features:**
- Detecção automática de paywall
- Limpeza de texto
- Normalização de datas
- Validação de conteúdo
- Logging detalhado
- Metadados de extração

**Article.extra contém:**
```python
{
    "extractor": "trafilatura",           # Método usado
    "confidence": 0.85,                   # Confiança
    "quality_score": 0.82,                # Score de qualidade
    "has_paywall": False,                 # Paywall detectado?
    "paywall_confidence": 0.0,            # Confiança do paywall
    "text_length": 1523,                  # Tamanho do texto
}
```

## Fluxo de Extração

```
1. ExtractionPipeline.extract(html, url)
   ├─> CustomSelectorExtractor (se domínio conhecido)
   ├─> TrafilaturaExtractor
   ├─> Newspaper3kExtractor
   ├─> ReadabilityExtractor
   └─> BeautifulSoupExtractor (sempre funciona)

2. Para cada extrator:
   ├─> Tenta extrair
   ├─> Calcula quality_score
   ├─> Se score >= 0.8: retorna imediatamente
   └─> Se score < threshold: tenta próximo

3. Pós-processamento:
   ├─> PaywallDetector.detect()
   ├─> TextCleaner.clean()
   ├─> DateNormalizer.normalize()
   └─> ContentValidator.validate()

4. Retorna melhor resultado
```

## Exemplo Completo

```python
from news_scraper.extractors import ExtractionPipeline
from news_scraper.tools import (
    PaywallDetector,
    TextCleaner,
    ContentValidator,
    UserAgentRotator,
    DomainRateLimiter,
    RetryStrategy,
)
import requests

# Setup
pipeline = ExtractionPipeline()
ua_rotator = UserAgentRotator()
rate_limiter = DomainRateLimiter(default_delay=2.0)
retry_strategy = RetryStrategy()
paywall_detector = PaywallDetector()
text_cleaner = TextCleaner()
validator = ContentValidator()

def scrape_article(url: str):
    # Rate limiting
    domain = extract_domain(url)
    rate_limiter.wait(domain)
    
    # Fetch com retry
    def fetch():
        headers = ua_rotator.get_browser_headers()
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return response.text
    
    html = retry_strategy.execute(fetch)
    
    # Extrair
    result = pipeline.extract(html, url, min_quality=0.3)
    
    if not result:
        raise ValueError("Extraction failed")
    
    # Detectar paywall
    paywall_info = paywall_detector.detect(html, result.text)
    if paywall_info['has_paywall'] and paywall_info['confidence'] > 0.7:
        print(f"⚠️  Paywall detected: {url}")
    
    # Limpar texto
    clean_text = text_cleaner.remove_boilerplate(result.text)
    clean_text = text_cleaner.clean(clean_text)
    
    # Validar
    if not validator.validate_title(result.title):
        print(f"⚠️  Invalid title: {result.title}")
    
    if not validator.validate_text(clean_text):
        print(f"⚠️  Invalid text length: {len(clean_text)}")
    
    return {
        "url": url,
        "title": result.title,
        "text": clean_text,
        "date": result.date,
        "authors": result.authors,
        "extractor": result.extractor,
        "confidence": result.confidence,
        "has_paywall": paywall_info['has_paywall'],
    }
```

## Configuração por Domínio

```python
# Seletores customizados para sites conhecidos
CUSTOM_SELECTORS = {
    "infomoney.com.br": {
        "title": "h1.article-title, h1.entry-title",
        "text": "div.article-body p, div.entry-content p",
        "date": "time.published, meta[property='article:published_time']",
        "author": "span.author-name, a.author-link",
    },
    "moneytimes.com.br": {
        "title": "h1.post-title",
        "text": "div.post-content p",
        "date": "time.entry-date",
        "author": "span.author",
    },
    "valor.globo.com": {
        "title": "h1.content-head__title",
        "text": "article.content p",
        "date": "time",
    },
}

# Rate limits por domínio
DOMAIN_DELAYS = {
    "valor.globo.com": 5.0,      # Mais restritivo
    "bloomberg.com": 4.0,
    "infomoney.com.br": 2.0,     # Padrão
    "moneytimes.com.br": 2.0,
}
```

## Métricas e Monitoramento

Cada extração gera métricas:

```python
{
    "extractor_used": "trafilatura",
    "extraction_time": 1.23,
    "quality_score": 0.85,
    "confidence": 0.82,
    "text_length": 1523,
    "paragraph_count": 12,
    "has_title": True,
    "has_date": True,
    "has_author": True,
    "has_paywall": False,
    "validation_passed": True,
}
```

## Testes

```bash
# Testar extratores
pytest tests/test_extractors.py -v

# Testar ferramentas
pytest tests/test_tools.py -v

# Testar integração
pytest tests/test_extract.py -v
```

## Vantagens da Arquitetura

1. **Robustez**: Múltiplos fallbacks garantem sucesso
2. **Qualidade**: Scores automáticos validam extração
3. **Flexibilidade**: Seletores customizados por site
4. **Profissional**: Rate limiting, retry, cache, anti-bot
5. **Observabilidade**: Métricas detalhadas de cada extração
6. **Manutenibilidade**: Módulos independentes e testáveis
7. **Escalabilidade**: Fácil adicionar novos extratores
8. **Compliance**: Respeita robots.txt, rate limits

## Próximos Passos

- [ ] Adicionar mais extratores (goose3, html2text)
- [ ] Cache distribuído (Redis)
- [ ] Monitoramento com Prometheus
- [ ] Dashboard de qualidade
- [ ] ML para detectar conteúdo principal
- [ ] Suporte a JavaScript rendering
- [ ] Proxy rotation automático
- [ ] Detecção de captcha
