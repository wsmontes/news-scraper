from __future__ import annotations

from dataclasses import dataclass

import feedparser


@dataclass(slots=True)
class RssItem:
    url: str
    title: str | None = None


def collect_links_from_feed(feed_url: str, limit: int | None = None) -> list[RssItem]:
    parsed = feedparser.parse(feed_url)
    items: list[RssItem] = []
    for entry in parsed.entries:
        link = getattr(entry, "link", None)
        if not link:
            continue
        title = getattr(entry, "title", None)
        items.append(RssItem(url=link, title=title))
        if limit is not None and len(items) >= limit:
            break
    return items
