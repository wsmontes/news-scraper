#!/bin/bash
# Exemplos de uso do CLI do news-scraper

echo "=========================================="
echo "EXEMPLOS DE USO DO NEWS-SCRAPER CLI"
echo "=========================================="

# 1. Coletar InfoMoney - últimas notícias
echo -e "\n1. Coletar 10 artigos do InfoMoney (categoria mercados):"
echo "   news-scraper collect --source infomoney --category mercados --limit 10 --skip-scrape --urls-out data/raw/infomoney_urls.txt"

# 2. Coletar múltiplas fontes
echo -e "\n2. Coletar de múltiplas fontes de uma vez:"
echo "   news-scraper collect --source infomoney --source moneytimes --source valor --limit 5"

# 3. Coletar todas as fontes
echo -e "\n3. Coletar de TODAS as fontes:"
echo "   news-scraper collect --source all --limit 10"

# 4. Coletar com filtro de data
echo -e "\n4. Coletar e filtrar por período:"
echo "   news-scraper collect --source infomoney --limit 50 --start-date 2026-01-01 --end-date 2026-01-28"

# 5. Coletar com proxies
echo -e "\n5. Coletar usando sistema inteligente de proxies:"
echo "   news-scraper collect --source all --limit 10 --use-proxy --verbose"

# 6. Apenas coletar URLs (sem scrape)
echo -e "\n6. Apenas coletar URLs sem fazer scrape:"
echo "   news-scraper collect --source bloomberg --category mercados --limit 20 --skip-scrape --urls-out data/raw/bloomberg_urls.txt"

# 7. Consultar dataset
echo -e "\n7. Consultar artigos coletados:"
echo "   news-scraper query --dataset-dir data/processed/articles --sql \"SELECT source, COUNT(*) as total FROM articles GROUP BY source\""

# 8. Estatísticas do dataset
echo -e "\n8. Ver estatísticas do dataset:"
echo "   news-scraper stats --dataset-dir data/processed/articles"

# 9. Coletar fonte específica com browser
echo -e "\n9. Coletar Valor Econômico (comando browser):"
echo "   news-scraper browser valor --category mercados --limit 15 --out data/raw/valor_urls.txt --scrape --dataset-dir data/processed/articles"

# 10. Workflow completo
echo -e "\n10. WORKFLOW COMPLETO - Coleta + Análise:"
cat << 'EOF'
   # Passo 1: Coletar de todas as fontes
   news-scraper collect --source all --limit 20 --urls-out data/raw/all_sources.txt

   # Passo 2: Ver estatísticas
   news-scraper stats --dataset-dir data/processed/articles

   # Passo 3: Consultar por fonte
   news-scraper query --dataset-dir data/processed/articles \
     --sql "SELECT source, date, title FROM articles WHERE date >= '2026-01-20' ORDER BY date DESC LIMIT 10"

   # Passo 4: Filtrar por palavra-chave
   news-scraper query --dataset-dir data/processed/articles \
     --sql "SELECT title, source FROM articles WHERE LOWER(text) LIKE '%juros%' LIMIT 5"
EOF

echo -e "\n=========================================="
echo "EXEMPLOS PRÁTICOS"
echo "=========================================="

# Exemplo real 1: Análise semanal
echo -e "\n📊 EXEMPLO: Análise semanal de notícias de mercado"
cat << 'EOF'
# Coletar notícias da semana de todas as fontes
news-scraper collect \
  --source all \
  --category mercados \
  --limit 30 \
  --start-date 2026-01-20 \
  --end-date 2026-01-28 \
  --dataset-dir data/processed/weekly \
  --use-proxy \
  --verbose

# Analisar distribuição por fonte
news-scraper query \
  --dataset-dir data/processed/weekly \
  --sql "SELECT source, COUNT(*) as artigos FROM articles GROUP BY source ORDER BY artigos DESC"

# Top palavras-chave
news-scraper query \
  --dataset-dir data/processed/weekly \
  --sql "SELECT LOWER(REGEXP_EXTRACT(text, '\\w+', 0)) as palavra, COUNT(*) as freq FROM articles GROUP BY palavra ORDER BY freq DESC LIMIT 20"
EOF

# Exemplo real 2: Monitoramento diário
echo -e "\n📅 EXEMPLO: Monitoramento diário automático"
cat << 'EOF'
#!/bin/bash
# Script para rodar diariamente (cron)

TODAY=$(date +%Y-%m-%d)
OUTDIR="data/daily/$TODAY"

mkdir -p "$OUTDIR"

news-scraper collect \
  --source all \
  --limit 50 \
  --dataset-dir "$OUTDIR/articles" \
  --urls-out "$OUTDIR/urls.txt" \
  --use-proxy \
  --delay 3.0 \
  --verbose > "$OUTDIR/log.txt" 2>&1

# Gerar relatório
news-scraper query \
  --dataset-dir "$OUTDIR/articles" \
  --sql "SELECT source, COUNT(*) FROM articles GROUP BY source" \
  --format csv > "$OUTDIR/report.csv"

echo "Coleta diária concluída: $TODAY"
EOF

echo -e "\n=========================================="
echo "DICAS E BOAS PRÁTICAS"
echo "=========================================="

cat << 'EOF'
1. 🎯 FONTES:
   - InfoMoney: Melhor para mercados financeiros brasileiros
   - Money Times: Foco em investimentos e economia
   - Valor: Jornal econômico tradicional
   - Bloomberg: Visão internacional dos mercados
   - E-Investidor: Foco em investidor pessoa física

2. 🚀 PERFORMANCE:
   - Use --use-proxy para evitar bloqueios
   - Ajuste --delay para respeitar rate limits
   - Use --limit para testes, depois aumente
   - --headless=true é mais rápido

3. 📅 FILTROS DE DATA:
   - --start-date/--end-date filtra APÓS coleta
   - Para histórico, use comando 'historical generate'
   - Datas no formato ISO: YYYY-MM-DD

4. 💾 ARMAZENAMENTO:
   - Dataset Parquet é particionado por data
   - Use --urls-out para backup de URLs
   - --skip-scrape útil para validar URLs primeiro

5. 🔍 ANÁLISE:
   - Use DuckDB SQL para consultas rápidas
   - Format=csv para exportar para Excel
   - stats mostra overview completo

6. 🤖 AUTOMAÇÃO:
   - Crie scripts para coleta periódica
   - Use cron para execução automática
   - Monitore logs com --verbose
EOF

echo -e "\n=========================================="
echo "COMANDOS ÚTEIS"
echo "=========================================="

cat << 'EOF'
# Ver todas as opções
news-scraper --help
news-scraper collect --help

# Teste rápido (5 artigos sem scrape)
news-scraper collect --source infomoney --limit 5 --skip-scrape --urls-out test.txt

# Coleta completa com todas as proteções
news-scraper collect \
  --source all \
  --limit 20 \
  --use-proxy \
  --proxy-fallback \
  --delay 2.0 \
  --headless \
  --verbose

# Consulta SQL customizada
news-scraper query \
  --dataset-dir data/processed/articles \
  --sql "SELECT * FROM articles WHERE source='InfoMoney' AND date='2026-01-28'" \
  --format csv > infomoney_hoje.csv

# Gerenciar fontes RSS
news-scraper sources list
news-scraper sources add --id myfeed --name "Meu Feed" --type rss --url "https://..."
news-scraper sources enable myfeed
EOF

echo -e "\n=========================================="
echo "Pronto para usar! 🚀"
echo "=========================================="
