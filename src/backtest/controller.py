"""Controller responsible for orchestrating the backtest workflow."""
from __future__ import annotations

from typing import Sequence

from .config import ControllerConfig
from .error_handling import ErrorContext, ErrorHandler
from .models import KBar, StrategyInsight
from .ports import KBarGateway, Reporter, Strategy


class BacktestController:
    """Coordinates data retrieval, strategy evaluation, and reporting."""

    def __init__(
        self,
        config: ControllerConfig,
        gateway: KBarGateway,
        strategy: Strategy,
        reporter: Reporter,
        error_handler: ErrorHandler | None = None,
    ) -> None:
        self._config = config
        self._gateway = gateway
        self._strategy = strategy
        self._reporter = reporter
        self._error_handler = error_handler or ErrorHandler()

    def run(self) -> None:
        stage = "validate_config"
        try:
            print("[Controller] 開始執行流程")
            self._config.validate()
            stage = "load_bars"
            bars = self._load_bars()
            stage = "analyze"
            insight = self._analyze(bars)
            stage = "report"
            self._report(insight)
            print("[Controller] 流程完成")
        except Exception as error:  # noqa: BLE001 - 統一交由 ErrorHandler 處理
            self._handle_error(error, stage)

    def _load_bars(self) -> Sequence[KBar]:
        print(
            f"[Controller] 從資料庫讀取 {self._config.stock_code} 最近 "
            f"{self._config.lookback} 根 K 棒"
        )
        bars = list(
            self._gateway.fetch_recent(
                stock_code=self._config.stock_code, limit=self._config.lookback
            )
        )
        if not bars:
            raise RuntimeError("讀取不到任何 K 棒資料，請確認股票代碼是否正確")
        print(f"[Controller] 成功載入 {len(bars)} 根 K 棒")
        return bars

    def _analyze(self, bars: Sequence[KBar]) -> StrategyInsight:
        print("[Controller] 執行策略分析")
        insight = self._strategy.evaluate(bars)
        print(
            "[Controller] 策略分析完成，最近收盤價 "
            f"{insight.last_close:.2f}, 漲跌幅 {insight.price_change_pct:.2f}%"
        )
        return insight

    def _report(self, insight: StrategyInsight) -> None:
        print("[Controller] 紀錄輸出資訊")
        self._reporter.report(insight)

    def _handle_error(self, error: Exception, stage: str) -> None:
        context = ErrorContext(stage=stage, stock_code=self._config.stock_code)
        self._error_handler.capture(error, context)
