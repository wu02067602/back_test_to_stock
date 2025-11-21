"""Configuration objects for the backtest controller."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ControllerConfig:
    """Configuration required to run the backtest controller."""

    db_path: Path
    stock_code: str
    lookback: int = 120

    def validate(self) -> None:
        """Validate that the provided configuration is usable."""
        if self.lookback <= 0:
            raise ValueError("lookback 必須為正整數")
        if not self.db_path.exists():
            raise FileNotFoundError(f"找不到資料庫檔案: {self.db_path}")
        if not self.db_path.is_file():
            raise FileNotFoundError(f"指定的資料庫路徑不是檔案: {self.db_path}")
        if not self.stock_code:
            raise ValueError("stock_code 不可為空")
