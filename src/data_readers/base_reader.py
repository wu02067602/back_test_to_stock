"""資料讀取相關的抽象類別定義。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Optional, Protocol, Sequence

import pandas as pd


class SupportsDictLike(Protocol):
    """允許傳入 dict-like 參數的簡易協定。"""

    def items(self) -> Iterable[tuple[str, object]]:
        """回傳 key/value 迭代器。"""


class AbstractDataReader(ABC):
    """資料讀取的抽象定義，回傳值需要是 pandas.DataFrame。"""

    @abstractmethod
    def read(  # noqa: D401 - 依照 coding-style 只提供簡短說明
        self,
        columns: Optional[Sequence[str]] = None,
        filters: Optional[Mapping[str, object] | SupportsDictLike] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        讀取資料並回傳 DataFrame。

        :param columns: 指定要讀取的欄位，預設為全部欄位。
        :param filters: 提供欄位條件的 mapping 物件，實作需自行決定支援方式。
        :param limit: 限制輸出的筆數。
        """


class BaseSqlDataReader(AbstractDataReader):
    """提供 SQL 型資料庫共用的檔案路徑驗證邏輯。"""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path).expanduser().resolve()
        if not self._database_path.exists():
            raise FileNotFoundError(f"找不到資料庫檔案：{self._database_path}")

    @property
    def database_path(self) -> Path:
        """取得資料庫檔案的絕對路徑。"""

        return self._database_path

    @staticmethod
    def _validate_limit(limit: Optional[int]) -> None:
        if limit is None:
            return
        if limit <= 0:
            raise ValueError("limit 參數必須是正整數")


def normalize_filters(
    filters: Optional[Mapping[str, object] | SupportsDictLike],
) -> MutableMapping[str, object]:
    """將過濾條件統一轉為 dict，方便後續建構 SQL where 子句。"""

    if filters is None:
        return {}
    if isinstance(filters, Mapping):
        return dict(filters)
    return dict(filters.items())
