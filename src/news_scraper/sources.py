from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Source:
    enabled: bool
    source_id: str
    name: str
    type: str
    url: str
    tags: list[str]


def _parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    v = value.strip().lower()
    return v in {"1", "true", "yes", "y", "sim"}


def _parse_tags(value: str | None) -> list[str]:
    if not value:
        return []
    # Aceita ; ou ,
    raw = value.replace(",", ";")
    return [t.strip() for t in raw.split(";") if t.strip()]


def load_sources_csv(path: Path) -> list[Source]:
    """Carrega fontes de um CSV simples.

    Linhas vazias e comentários (iniciando com #) são ignorados.
    """

    text = path.read_text(encoding="utf-8")
    # Filtra comentários mantendo header
    lines: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            continue
        lines.append(line)

    if not lines:
        return []

    reader = csv.DictReader(lines)
    sources: list[Source] = []
    for row in reader:
        enabled = _parse_bool(row.get("enabled"))
        source_id = (row.get("source_id") or "").strip()
        name = (row.get("name") or "").strip()
        type_ = (row.get("type") or "").strip().lower()
        url = (row.get("url") or "").strip()
        tags = _parse_tags(row.get("tags"))

        if not url or not type_:
            continue
        if not source_id:
            # fallback estável: usa nome se existir, senão url
            source_id = (name or url)[:64]

        sources.append(
            Source(
                enabled=enabled,
                source_id=source_id,
                name=name or source_id,
                type=type_,
                url=url,
                tags=tags,
            )
        )

    return sources


def enabled_rss_feeds(sources: list[Source]) -> list[str]:
    return [s.url for s in sources if s.enabled and s.type == "rss"]
