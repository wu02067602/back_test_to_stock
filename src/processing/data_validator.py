"""提供 K 線資料的驗證與統計功能。"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import time
from typing import Dict, Mapping
from zoneinfo import ZoneInfo

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ValidationReport:
    """儲存驗證結果與各種異常的筆數。"""

    issues: Mapping[str, int]

    @property
    def is_valid(self) -> bool:
        """若所有異常筆數皆為 0，則視為驗證通過。"""

        return all(count == 0 for count in self.issues.values())

    @property
    def total_invalid_rows(self) -> int:
        """取得所有異常筆數的總和。"""

        return sum(self.issues.values())

    def to_dict(self) -> Dict[str, int]:
        """將結果轉成一般 dict，方便序列化或測試。"""

        return dict(self.issues)


class KbarDataValidator:
    """執行價格、成交量、空值與交易時段的驗證。"""

    REQUIRED_PRICE_COLUMNS = ("Open", "High", "Low", "Close")
    VOLUME_COLUMN = "Volume"

    def __init__(
        self,
        *,
        timestamp_column: str = "ts",
        timezone: str = "Asia/Taipei",
        trading_start: time = time(9, 0, 0),
        trading_end: time = time(15, 0, 0),
    ) -> None:
        self._timestamp_column = timestamp_column
        self._timezone = ZoneInfo(timezone)
        self._trading_start = trading_start
        self._trading_end = trading_end

    def validate(self, frame: pd.DataFrame) -> ValidationReport:
        """
        檢查 DataFrame 是否符合交易規則，並回傳統計結果。

        :param frame: 欲檢查的 DataFrame
        """

        self._ensure_required_columns(frame)
        issues = {
            "non_positive_prices": self._count_non_positive_prices(frame),
            "negative_volume": self._count_negative_volume(frame),
            "rows_with_null": self._count_rows_with_null(frame),
            "non_trading_time_rows": self._count_rows_outside_trading_time(frame),
        }

        invalid_time_count = issues["non_trading_time_rows"]
        logger.warning("非交易時段資料筆數：%s", invalid_time_count)

        return ValidationReport(issues=issues)

    def _ensure_required_columns(self, frame: pd.DataFrame) -> None:
        missing_columns = [
            column
            for column in (*self.REQUIRED_PRICE_COLUMNS, self.VOLUME_COLUMN, self._timestamp_column)
            if column not in frame.columns
        ]
        if missing_columns:
            raise KeyError(f"資料中缺少必填欄位：{', '.join(missing_columns)}")

    def _count_non_positive_prices(self, frame: pd.DataFrame) -> int:
        mask = pd.Series(False, index=frame.index)
        for column in self.REQUIRED_PRICE_COLUMNS:
            mask |= frame[column] <= 0
        return int(mask.sum())

    def _count_negative_volume(self, frame: pd.DataFrame) -> int:
        return int((frame[self.VOLUME_COLUMN] < 0).sum())

    def _count_rows_with_null(self, frame: pd.DataFrame) -> int:
        return int(frame.isna().any(axis=1).sum())

    def _count_rows_outside_trading_time(self, frame: pd.DataFrame) -> int:
        series = pd.to_datetime(frame[self._timestamp_column], errors="coerce")
        series = self._ensure_timezone(series)
        invalid_mask = series.isna() | ~self._is_within_trading_time(series)
        return int(invalid_mask.sum())

    def _ensure_timezone(self, series: pd.Series) -> pd.Series:
        if series.dt.tz is None:
            return series.dt.tz_localize(self._timezone)
        return series.dt.tz_convert(self._timezone)

    def _is_within_trading_time(self, series: pd.Series) -> pd.Series:
        seconds = (
            series.dt.hour * 3600 + series.dt.minute * 60 + series.dt.second
        )
        start_seconds = (
            self._trading_start.hour * 3600
            + self._trading_start.minute * 60
            + self._trading_start.second
        )
        end_seconds = (
            self._trading_end.hour * 3600
            + self._trading_end.minute * 60
            + self._trading_end.second
        )
        return (seconds >= start_seconds) & (seconds <= end_seconds)
