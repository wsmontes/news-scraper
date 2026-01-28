#!/bin/bash
# Script de teste: Coleta inicial de notícias financeiras

set -e

echo "=== Teste: Coleta de Notícias Financeiras ==="
echo ""

# Diretórios
mkdir -p data/raw data/interim outputs

echo "1. Testando RSS do InfoMoney (últimas notícias)..."
./.venv/bin/python -m news_scraper rss \
  --feed "https://www.infomoney.com.br/feed/" \
  --scrape \
  --out outputs/test_infomoney.jsonl \
  --limit 5 \
  --delay 2.0

echo ""
echo "2. Verificando artigos coletados..."
if [ -f outputs/test_infomoney.jsonl ]; then
    count=$(wc -l < outputs/test_infomoney.jsonl)
    echo "   ✓ Coletados $count artigos"
    echo ""
    echo "   Primeiros títulos:"
    head -3 outputs/test_infomoney.jsonl | ./.venv/bin/python -c "
import sys, json
for line in sys.stdin:
    obj = json.loads(line)
    print(f\"   - {obj.get('title', 'N/A')[:80]}\")
"
else
    echo "   ✗ Arquivo não criado"
    exit 1
fi

echo ""
echo "3. Testando coleta para dataset Parquet..."
./.venv/bin/python -m news_scraper rss \
  --feed "https://www.infomoney.com.br/feed/" \
  --scrape \
  --dataset-dir data/processed/articles \
  --limit 3 \
  --delay 2.0

echo ""
echo "4. Verificando dataset..."
if [ -d data/processed/articles ]; then
    parquet_files=$(find data/processed/articles -name "*.parquet" | wc -l)
    echo "   ✓ Arquivos Parquet criados: $parquet_files"
    
    echo ""
    echo "5. Consultando dataset com DuckDB..."
    ./.venv/bin/python -m news_scraper stats --dataset-dir data/processed/articles
else
    echo "   ✗ Dataset não criado"
    exit 1
fi

echo ""
echo "=== ✓ Teste concluído com sucesso! ==="
echo ""
echo "Próximos passos:"
echo "  - Veja os artigos em: outputs/test_infomoney.jsonl"
echo "  - Dataset Parquet em: data/processed/articles/"
echo "  - Para histórico, use: bash scripts/collect_historical.sh"
