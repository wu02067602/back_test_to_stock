"""SQLite 版本的資料讀取實作。"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Mapping, MutableMapping, Sequence

import pandas as pd

from .base_reader import BaseSqlDataReader, normalize_filters


class SQLiteDataReader(BaseSqlDataReader):
    """從 SQLite 資料庫讀取資料並轉為 pandas.DataFrame。"""

    def __init__(
        self,
        database_path: str | Path,
        table_name: str = "daily_kbars",
    ) -> None:
        super().__init__(database_path)
        self._table_name = table_name

    def read(
        self,
        columns: Sequence[str] | None = None,
        filters: Mapping[str, object] | None = None,
        limit: int | None = None,
    ) -> pd.DataFrame:
        """執行查詢並回傳 DataFrame。"""

        self._validate_limit(limit)
        query, params = self._build_query(columns, filters, limit)
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            return pd.read_sql_query(query, connection, params=params)

    def _build_query(
        self,
        columns: Sequence[str] | None,
        filters: Mapping[str, object] | None,
        limit: int | None,
    ) -> tuple[str, MutableMapping[str, object]]:
        selected_columns = ", ".join(columns) if columns else "*"
        where_clause, params = self._build_where_clause(filters)
        suffix = f" LIMIT {limit}" if limit else ""
        query = f"SELECT {selected_columns} FROM {self._table_name}{where_clause}{suffix};"
        return query, params

    def _build_where_clause(
        self,
        filters: Mapping[str, object] | None,
    ) -> tuple[str, MutableMapping[str, object]]:
        normalized = normalize_filters(filters)
        if not normalized:
            return "", {}

        expressions = []
        params: MutableMapping[str, object] = {}
        for idx, (column, value) in enumerate(normalized.items()):
            param_name = f"param_{idx}"
            if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                value_list = list(value)
                placeholders = ", ".join(f":{param_name}_{i}" for i in range(len(value_list)))
                expressions.append(f"{column} IN ({placeholders})")
                for i, item in enumerate(value_list):
                    params[f"{param_name}_{i}"] = item
            else:
                expressions.append(f"{column} = :{param_name}")
                params[param_name] = value

        clause = " WHERE " + " AND ".join(expressions)
        return clause, params
