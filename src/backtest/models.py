"""Data models used throughout the backtest controller."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class KBar:
    """Represents one minute-k bar row."""

    timestamp: datetime
    stock_code: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int


@dataclass(frozen=True)
class StrategyInsight:
    """Result returned by a strategy evaluation run."""

    stock_code: str
    total_volume: int
    average_close: float
    last_close: float
    price_change_pct: float
    verdict: str
