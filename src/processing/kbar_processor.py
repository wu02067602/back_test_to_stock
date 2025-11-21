"""提供 K 線資料時間欄位處理的工具。"""
from __future__ import annotations

from dataclasses import dataclass
from zoneinfo import ZoneInfo

import pandas as pd


@dataclass(frozen=True)
class TimestampProcessingConfig:
    """時間欄位處理的設定值。"""

    timestamp_column: str = "ts"
    source_timezone: str = "UTC"
    target_timezone: str = "Asia/Taipei"


class KbarDataProcessor:
    """負責驗證並轉換 DataFrame 中的時間欄位。"""

    def __init__(self, config: TimestampProcessingConfig | None = None) -> None:
        self._config = config or TimestampProcessingConfig()
        self._source_tz = ZoneInfo(self._config.source_timezone)
        self._target_tz = ZoneInfo(self._config.target_timezone)

    @property
    def config(self) -> TimestampProcessingConfig:
        """取得目前使用的設定。"""

        return self._config

    def validate_timestamp_column(self, frame: pd.DataFrame) -> None:
        """確認時間欄位存在，並確保在轉換前不包含空值。"""

        column = self._config.timestamp_column
        if column not in frame.columns:
            raise KeyError(f"資料中缺少時間欄位：{column}")
        if frame[column].isna().any():
            raise ValueError("時間欄位包含空值，請先補齊資料後再處理。")

    def convert_timezone(self, frame: pd.DataFrame, *, inplace: bool = False) -> pd.DataFrame:
        """
        將時間欄位自來源時區轉換到目標時區。

        :param frame: 需處理的 DataFrame
        :param inplace: 若為 True 則直接修改輸入的 DataFrame
        :return: 已轉換時間欄位的 DataFrame
        """

        self.validate_timestamp_column(frame)
        target_frame = frame if inplace else frame.copy()

        column = self._config.timestamp_column
        series = pd.to_datetime(target_frame[column], errors="raise")
        if series.dt.tz is None:
            localized = series.dt.tz_localize(self._source_tz)
        else:
            localized = series.dt.tz_convert(self._source_tz)
        target_frame[column] = localized.dt.tz_convert(self._target_tz)
        return target_frame

    def process(self, frame: pd.DataFrame, *, inplace: bool = False) -> pd.DataFrame:
        """
        單一介面，便於外部呼叫進行時間欄位轉換。

        :param frame: 需處理的 DataFrame
        :param inplace: 若為 True 則直接修改輸入的 DataFrame
        :return: 已轉換時間欄位的 DataFrame
        """

        return self.convert_timezone(frame, inplace=inplace)
