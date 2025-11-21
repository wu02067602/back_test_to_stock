"""Reporting utilities for controller output."""
from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from .models import StrategyInsight
from .ports import Reporter


class ConsoleReporter(Reporter):
    """Prints strategy insights to stdout."""

    def __init__(self, *, emit_raw: bool = False) -> None:
        self._emit_raw = emit_raw

    def report(self, insight: StrategyInsight) -> None:
        if self._emit_raw:
            print("[Insight]", asdict(insight))
            return
        self._print_human_friendly(insight)

    def _print_human_friendly(self, insight: StrategyInsight) -> None:
        print("=== 策略輸出摘要 ===")
        print(f"股票代碼: {insight.stock_code}")
        print(f"總成交量: {self._format_large_number(insight.total_volume)}")
        print(f"平均收盤價: {insight.average_close:.2f}")
        print(f"最後收盤價: {insight.last_close:.2f}")
        print(f"期間漲跌幅: {insight.price_change_pct:.2f}%")
        print(f"策略判斷: {insight.verdict}")

    @staticmethod
    def _format_large_number(value: int) -> str:
        units: Iterable[tuple[int, str]] = (
            (10**8, "億"),
            (10**4, "萬"),
        )
        for threshold, label in units:
            if value >= threshold:
                return f"{value / threshold:.2f}{label}"
        return str(value)
