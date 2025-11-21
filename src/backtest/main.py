"""Command line entry-point for running the controller."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

from .config import ControllerConfig
from .controller import BacktestController
from .error_handling import ErrorHandler
from .reporting import ConsoleReporter
from .sqlite_gateway import SqliteKBarGateway
from .strategy import MomentumStrategy


def main(argv: Sequence[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    controller = _build_controller(args)
    controller.run()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the backtest controller")
    parser.add_argument(
        "--db-path",
        default=_default_db_path(),
        type=Path,
        help="SQLite 資料庫路徑，預設為專案根目錄的 sample_kbars.db",
    )
    parser.add_argument(
        "--stock-code",
        default="2330",
        help="要分析的股票代碼",
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=120,
        help="要回溯的 K 棒數量",
    )
    parser.add_argument(
        "--raw-output",
        action="store_true",
        help="是否輸出原始資料結構，預設為 False",
    )
    return parser


def _build_controller(args: argparse.Namespace) -> BacktestController:
    config = ControllerConfig(
        db_path=args.db_path,
        stock_code=args.stock_code,
        lookback=args.lookback,
    )
    gateway = SqliteKBarGateway(config.db_path)
    strategy = MomentumStrategy()
    reporter = ConsoleReporter(emit_raw=args.raw_output)
    error_handler = ErrorHandler()
    return BacktestController(
        config=config,
        gateway=gateway,
        strategy=strategy,
        reporter=reporter,
        error_handler=error_handler,
    )


def _default_db_path() -> Path:
    return Path(__file__).resolve().parents[2] / "sample_kbars.db"


if __name__ == "__main__":
    main()
