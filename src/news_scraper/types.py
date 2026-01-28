from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Article:
    url: str
    title: str | None = None
    author: str | None = None
    date_published: datetime | None = None
    scraped_at: datetime | None = None
    text: str | None = None
    language: str | None = None
    source: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
