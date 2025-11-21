"""SQLite implementation of the K-bar gateway."""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .models import KBar
from .ports import KBarGateway


class SqliteKBarGateway(KBarGateway):
    """Reads k-bar data from a SQLite database."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = Path(db_path)

    def fetch_recent(self, stock_code: str, limit: int) -> Sequence[KBar]:
        query = (
            "SELECT ts, stock_code, Open, High, Low, Close, Volume "
            "FROM daily_kbars WHERE stock_code = ? ORDER BY ts DESC LIMIT ?"
        )
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, (stock_code, limit)).fetchall()
        return [self._row_to_model(row) for row in rows]

    def _row_to_model(self, row: sqlite3.Row) -> KBar:
        ts = row["ts"]
        timestamp = (
            datetime.fromisoformat(ts)
            if isinstance(ts, str)
            else datetime.fromtimestamp(ts)
        )
        return KBar(
            timestamp=timestamp,
            stock_code=row["stock_code"],
            open_price=float(row["Open"]),
            high_price=float(row["High"]),
            low_price=float(row["Low"]),
            close_price=float(row["Close"]),
            volume=int(row["Volume"]),
        )
