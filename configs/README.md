# Configurações

Este diretório guarda arquivos fáceis de editar (CSV/YAML) para controlar o pipeline.

## sources.csv

Arquivo com a lista de fontes (RSS, sitemap, etc.). No momento o projeto usa esse CSV principalmente para **RSS**.

Campos suportados:

- `enabled`: `1` ou `0`
- `source_id`: identificador curto (ex.: `g1`, `folha`)
- `name`: nome amigável
- `type`: por enquanto use `rss`
- `url`: URL do feed RSS
- `tags`: opcional (ex.: `politica;economia`)

Exemplo:

```csv
enabled,source_id,name,type,url,tags
1,g1,G1,rss,https://g1.globo.com/rss/g1/,geral
0,exemplo,Exemplo,rss,https://example.com/rss.xml,teste
```
