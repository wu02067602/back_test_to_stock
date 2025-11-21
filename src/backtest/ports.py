"""Ports that define the boundaries between controller components."""
from __future__ import annotations

from typing import Protocol, Sequence

from .models import KBar, StrategyInsight


class KBarGateway(Protocol):
    """Abstracts the data source of K bars."""

    def fetch_recent(self, stock_code: str, limit: int) -> Sequence[KBar]:
        """Return the most recent *limit* k-bars for the specified stock."""


class Strategy(Protocol):
    """Defines a strategy that can evaluate a batch of k-bars."""

    def evaluate(self, bars: Sequence[KBar]) -> StrategyInsight:
        """Produce an insight based on the provided bars."""


class Reporter(Protocol):
    """Responsible for presenting strategy insights to end users."""

    def report(self, insight: StrategyInsight) -> None:
        """Emit the insight to the desired sink (console, file, etc.)."""
