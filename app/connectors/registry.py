"""Allowlisted connector registry — no open-web crawl, no DRM bypass."""

from __future__ import annotations

from typing import Dict, Type

from app.connectors.ao3_class import Ao3ClassConnector
from app.connectors.base import BaseConnector, ConnectorError
from app.connectors.manual_url import ManualUrlConnector
from app.connectors.private_library import PrivateLibraryConnector
from app.connectors.reddit_nsfw import RedditNsfwConnector

_REGISTRY: Dict[str, Type[BaseConnector]] = {
    ManualUrlConnector.name: ManualUrlConnector,
    Ao3ClassConnector.name: Ao3ClassConnector,
    PrivateLibraryConnector.name: PrivateLibraryConnector,
    RedditNsfwConnector.name: RedditNsfwConnector,
}


def list_connectors() -> list[str]:
    return sorted(_REGISTRY.keys())


def get_connector(name: str) -> BaseConnector:
    key = (name or "manual_url").strip().lower()
    if key not in _REGISTRY:
        raise ConnectorError(
            f"connector {name!r} not allowlisted; allowed: {', '.join(list_connectors())}"
        )
    return _REGISTRY[key]()
