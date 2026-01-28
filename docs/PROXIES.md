# Sistema de Proxies com Fallback Automático

## 📋 Implementado

### 1. ProxyManager (`proxy_manager.py`)
- ✅ 25 proxies gratuitos configurados
- ✅ Rotação automática entre proxies
- ✅ Sistema de marcação de falhas (max 3 falhas)
- ✅ Métodos de teste de conectividade
- ✅ Reset automático quando todos falham

### 2. Integração com Browser (`browser.py`)
- ✅ `BrowserConfig` com opções de proxy:
  - `use_proxy`: Ativa/desativa proxies
  - `proxy_fallback`: Tenta sem proxy se todos falharem
- ✅ Retry automático com fallback
- ✅ Troca de proxy em caso de falha

## 🚀 Uso

### Básico - Com Proxy
```python
from news_scraper.browser import BrowserConfig, ProfessionalScraper

config = BrowserConfig(
    headless=True,
    use_proxy=True,           # Ativa proxies
    proxy_fallback=True       # Fallback para sem proxy
)

with ProfessionalScraper(config) as scraper:
    scraper.get_page("https://exemplo.com")
```

### Com Scrapers
```python
from news_scraper import InfoMoneyScraper
from news_scraper.browser import BrowserConfig, ProfessionalScraper

config = BrowserConfig(use_proxy=True, proxy_fallback=True)

with ProfessionalScraper(config) as scraper:
    infomoney = InfoMoneyScraper(scraper)
    urls = infomoney.get_latest_articles(limit=10)
```

### Rotação Manual
```python
from news_scraper.proxy_manager import get_proxy_manager

pm = get_proxy_manager()

for i in range(5):
    proxy = pm.get_next_proxy()
    print(f"Usando: {proxy.url}")
    
    # Usar proxy...
    
    # Marcar sucesso ou falha
    pm.mark_success(proxy)  # ou pm.mark_failure(proxy)
```

## 🔄 Funcionamento do Fallback

1. **Tentativa 1**: Usa proxy da lista
2. **Se falhar**: Marca proxy como falho
3. **Tentativa 2**: Tenta próximo proxy
4. **Se falhar**: Marca e tenta próximo
5. **Tentativa 3**: Último proxy
6. **Se tudo falhar**: Tenta SEM proxy (fallback)

## 📊 Fontes de Proxies

25 proxies públicos de:
- Brasil (5)
- EUA (5)
- Europa (5)
- Ásia (5)
- América Latina (5)

**Nota**: Proxies gratuitos são instáveis. O sistema automaticamente:
- Rotaciona entre os disponíveis
- Marca os que falham 3x
- Reseta contadores quando todos falharem
- Faz fallback para conexão direta

## 🧪 Testar

```bash
# Teste completo
python scripts/test_proxies.py

# Exemplo com scrapers
python scripts/exemplo_proxies.py
```

## ⚙️ Configuração

### Adicionar Mais Proxies

Edite `proxy_manager.py`:
```python
FREE_PROXIES = [
    ("host", porta),
    # ... seus proxies
]
```

### Ajustar Tolerância

```python
pm = ProxyManager(max_failures=5)  # Permite 5 falhas antes de desabilitar
```

## 💡 Dicas

1. **Proxies gratuitos são instáveis**: Taxa de sucesso ~10-30%
2. **Use fallback**: Sempre habilite `proxy_fallback=True`
3. **Para produção**: Considere proxies pagos (mais estáveis)
4. **Testes periódicos**: `pm.test_all_proxies()` para verificar disponibilidade
5. **Rate limiting**: Proxies ajudam a evitar bloqueios por IP
