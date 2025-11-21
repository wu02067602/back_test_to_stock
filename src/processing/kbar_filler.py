"""提供補齊分鐘 K 線資料的工具。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import pandas as pd


@dataclass(frozen=True)
class KbarFillerConfig:
    """補值所需的欄位設定。"""

    timestamp_column: str = "ts"
    stock_code_column: str = "stock_code"
    ffill_columns: Sequence[str] = field(
        default_factory=lambda: ("Open", "High", "Low", "Close"),
    )
    zero_fill_columns: Sequence[str] = field(default_factory=lambda: ("Volume",))

    def all_required_columns(self) -> set[str]:
        """列出所有需要存在於 DataFrame 的欄位。"""

        return {
            self.timestamp_column,
            self.stock_code_column,
            *self.ffill_columns,
            *self.zero_fill_columns,
        }


class KbarDataFiller:
    """補齊每檔股票缺少的分鐘資料並以前值填補。"""

    def __init__(self, config: KbarFillerConfig | None = None) -> None:
        self._config = config or KbarFillerConfig()

    def fill(self, frame: pd.DataFrame) -> pd.DataFrame:
        """
        針對每個股票代碼補齊缺漏的分鐘資料。

        :param frame: 原始的 K 線資料。
        :return: 已補齊並依時間排序的 DataFrame。
        """

        self._ensure_required_columns(frame)

        working = frame.copy()
        ts_col = self._config.timestamp_column
        code_col = self._config.stock_code_column
        working[ts_col] = pd.to_datetime(working[ts_col], errors="raise")
        working = working.sort_values([code_col, ts_col])

        filled_frames = [
            self._fill_single_stock(stock_code, stock_df) for stock_code, stock_df in working.groupby(code_col)
        ]
        result = pd.concat(filled_frames, ignore_index=True).sort_values([code_col, ts_col])
        return result.reset_index(drop=True)

    def _fill_single_stock(self, stock_code: str, stock_df: pd.DataFrame) -> pd.DataFrame:
        ts_col = self._config.timestamp_column
        code_col = self._config.stock_code_column

        indexed = stock_df.set_index(ts_col)
        original_index = indexed.index
        full_index = pd.date_range(original_index.min(), original_index.max(), freq="1min", tz=original_index.tz)
        reindexed = indexed.reindex(full_index)

        columns_to_ffill = [
            column for column in reindexed.columns if column not in self._config.zero_fill_columns
        ]
        if columns_to_ffill:
            reindexed[columns_to_ffill] = reindexed[columns_to_ffill].ffill()

        is_new_row = ~reindexed.index.isin(original_index)
        for column in self._config.zero_fill_columns:
            reindexed.loc[is_new_row, column] = 0

        reindexed[code_col] = stock_code
        reindexed = reindexed.reset_index().rename(columns={"index": ts_col})
        return reindexed

    def _ensure_required_columns(self, frame: pd.DataFrame) -> None:
        missing = self._config.all_required_columns() - set(frame.columns)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise KeyError(f"資料中缺少補值所需欄位：{missing_str}")
