"""負責協調整個 K 線資料處理流程的 controller。"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import pandas as pd

from .data_readers.base_reader import AbstractDataReader
from .data_readers.sqlite_reader import SQLiteDataReader
from .processing.data_validator import KbarDataValidator, ValidationReport
from .processing.kbar_filler import KbarDataFiller
from .processing.kbar_processor import KbarDataProcessor

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PipelineArtifacts:
    """記錄處理過程中產生的各階段資料與驗證結果。"""

    raw_frame: pd.DataFrame
    timezone_aligned_frame: pd.DataFrame
    filled_frame: pd.DataFrame
    validation_report: ValidationReport


class KbarPipelineController:
    """串接資料讀取、驗證、時間轉換與補值邏輯。"""

    def __init__(
        self,
        data_reader: AbstractDataReader,
        validator: KbarDataValidator,
        processor: KbarDataProcessor,
        filler: KbarDataFiller,
        *,
        event_logger: logging.Logger | None = None,
    ) -> None:
        self._data_reader = data_reader
        self._validator = validator
        self._processor = processor
        self._filler = filler
        self._logger = event_logger or logger

    def run(
        self,
        *,
        columns: Sequence[str] | None = None,
        filters: Mapping[str, object] | None = None,
        limit: int | None = None,
    ) -> PipelineArtifacts:
        """
        依序執行資料讀取、驗證、時間轉換與補值。

        :param columns: 限制輸出欄位。
        :param filters: 查詢條件。
        :param limit: 限制讀取筆數。
        """

        self._logger.info("開始執行 KbarPipeline（limit=%s）", limit)
        raw_frame = self._read_data(columns, filters, limit)
        validation_report = self._validator.validate(raw_frame)
        self._log_validation(validation_report)
        timezone_aligned_frame = self._processor.process(raw_frame, inplace=False)
        self._logger.info("時間欄位轉換完成，目標時區：%s", self._processor.config.target_timezone)
        filled_frame = self._filler.fill(timezone_aligned_frame)
        self._logger.info("補值完成，總筆數：%s", len(filled_frame))
        return PipelineArtifacts(
            raw_frame=raw_frame,
            timezone_aligned_frame=timezone_aligned_frame,
            filled_frame=filled_frame,
            validation_report=validation_report,
        )

    def _read_data(
        self,
        columns: Sequence[str] | None,
        filters: Mapping[str, object] | None,
        limit: int | None,
    ) -> pd.DataFrame:
        frame = self._data_reader.read(columns=columns, filters=filters, limit=limit)
        self._logger.info("資料讀取完成，筆數：%s", len(frame))
        return frame

    def _log_validation(self, report: ValidationReport) -> None:
        if report.is_valid:
            self._logger.info("資料驗證通過，未發現異常。")
            return
        issues = report.to_dict()
        self._logger.warning("資料驗證發現異常：%s", issues)


def build_default_controller(
    database_path: str | Path,
    *,
    table_name: str = "daily_kbars",
) -> KbarPipelineController:
    """
    以預設組態建立 Controller，方便快速使用。

    :param database_path: SQLite 檔案路徑。
    :param table_name: 目標資料表名稱。
    """

    reader = SQLiteDataReader(database_path=database_path, table_name=table_name)
    validator = KbarDataValidator()
    processor = KbarDataProcessor()
    filler = KbarDataFiller()
    return KbarPipelineController(
        data_reader=reader,
        validator=validator,
        processor=processor,
        filler=filler,
    )


def configure_default_logging(level: int = logging.INFO) -> None:
    """提供簡單的 logging 設定，方便 CLI 或 Notebook 使用者引用。"""

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )
