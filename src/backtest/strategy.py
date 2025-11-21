"""Simple strategy implementation for demonstration purposes."""
from __future__ import annotations

from statistics import fmean
from typing import Sequence

from .models import KBar, StrategyInsight
from .ports import Strategy


class MomentumStrategy(Strategy):
    """Evaluates bars by comparing the latest and oldest closes."""

    def evaluate(self, bars: Sequence[KBar]) -> StrategyInsight:
        if not bars:
            raise ValueError("沒有可供分析的 K 棒資料")

        latest = bars[0]
        oldest = bars[-1]
        avg_close = fmean(bar.close_price for bar in bars)
        price_change_pct = (
            (latest.close_price - oldest.close_price) / oldest.close_price * 100
            if oldest.close_price
            else 0.0
        )
        verdict = self._decide_verdict(price_change_pct)
        total_volume = sum(bar.volume for bar in bars)
        return StrategyInsight(
            stock_code=latest.stock_code,
            total_volume=total_volume,
            average_close=avg_close,
            last_close=latest.close_price,
            price_change_pct=price_change_pct,
            verdict=verdict,
        )

    @staticmethod
    def _decide_verdict(price_change_pct: float) -> str:
        if price_change_pct > 3:
            return "趨勢偏多"
        if price_change_pct < -3:
            return "趨勢偏空"
        return "趨勢整理中"
