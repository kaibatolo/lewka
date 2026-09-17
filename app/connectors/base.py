"""Base connector interface for lewka.

Connectors normalize inbound metadata only. They MUST NOT download or
store media binaries. They MUST enforce age_proof before emit.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ConnectorError(ValueError):
    pass


class BaseConnector(ABC):
    name: str = "base"

    @abstractmethod
    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Return a metadata dict suitable for ingest (no binaries)."""

    def validate_allowlisted(self) -> None:
        """Hook for registry checks."""
        return None
