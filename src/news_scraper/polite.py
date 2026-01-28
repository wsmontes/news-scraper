from __future__ import annotations

import time
import urllib.parse
import urllib.robotparser
from dataclasses import dataclass

import requests


@dataclass
class PoliteSettings:
    delay_seconds: float = 1.0
    respect_robots: bool = True
    user_agent: str = "news-scraper-academic/0.1 (+https://example.invalid)"
    timeout_seconds: float = 20.0


class PoliteSession:
    def __init__(self, settings: PoliteSettings | None = None):
        self.settings = settings or PoliteSettings()
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.settings.user_agent})
        self._last_request_by_netloc: dict[str, float] = {}
        self._robots_by_netloc: dict[str, urllib.robotparser.RobotFileParser] = {}

    def _netloc(self, url: str) -> str:
        return urllib.parse.urlparse(url).netloc.lower()

    def _sleep_if_needed(self, netloc: str) -> None:
        delay = max(0.0, float(self.settings.delay_seconds))
        if delay <= 0:
            return
        last = self._last_request_by_netloc.get(netloc)
        if last is None:
            return
        elapsed = time.time() - last
        remaining = delay - elapsed
        if remaining > 0:
            time.sleep(remaining)

    def _robot_parser(self, url: str) -> urllib.robotparser.RobotFileParser:
        netloc = self._netloc(url)
        cached = self._robots_by_netloc.get(netloc)
        if cached is not None:
            return cached

        parsed = urllib.parse.urlparse(url)
        robots_url = urllib.parse.urlunparse((parsed.scheme, netloc, "/robots.txt", "", "", ""))
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
        except Exception:
            # Se falhar, seja conservador: permita apenas se o caller optar por ignorar robots.
            # Aqui mantemos como "sem regras" (RobotFileParser tende a permitir).
            pass
        self._robots_by_netloc[netloc] = rp
        return rp

    def allowed(self, url: str) -> bool:
        if not self.settings.respect_robots:
            return True
        rp = self._robot_parser(url)
        return rp.can_fetch(self.settings.user_agent, url)

    def get(self, url: str) -> requests.Response:
        netloc = self._netloc(url)
        self._sleep_if_needed(netloc)

        if self.settings.respect_robots and not self.allowed(url):
            raise PermissionError(f"Bloqueado por robots.txt: {url}")

        resp = self._session.get(url, timeout=self.settings.timeout_seconds)
        self._last_request_by_netloc[netloc] = time.time()
        resp.raise_for_status()
        return resp
