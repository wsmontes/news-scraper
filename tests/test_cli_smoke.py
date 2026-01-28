from __future__ import annotations

from news_scraper.cli import build_parser


def test_cli_builds_parser():
    p = build_parser()
    args = p.parse_args(["scrape", "--url", "https://example.com", "--out", "out.jsonl"])
    assert args.cmd == "scrape"
