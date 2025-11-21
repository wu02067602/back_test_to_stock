"""Centralized error handling utilities for the project."""
from __future__ import annotations

from dataclasses import dataclass


class ProjectError(RuntimeError):
    """Normalized exception type surfaced by the controller."""


@dataclass(frozen=True)
class ErrorContext:
    """Carries metadata describing where the error was raised."""

    stage: str
    stock_code: str


class ErrorHandler:
    """Formats and emits errors in a consistent manner."""

    def __init__(self, *, rethrow: bool = True) -> None:
        self._rethrow = rethrow

    def capture(self, error: Exception, context: ErrorContext) -> None:
        friendly_message = self._to_message(error)
        print("[Error] 發生錯誤，階段:", context.stage)
        print("[Error] 股票代碼:", context.stock_code)
        print("[Error] 詳細資訊:", friendly_message)
        if self._rethrow:
            raise self._normalize(error, friendly_message)

    @staticmethod
    def _to_message(error: Exception) -> str:
        return str(error) or error.__class__.__name__

    @staticmethod
    def _normalize(error: Exception, message: str) -> ProjectError:
        if isinstance(error, ProjectError):
            return error
        project_error = ProjectError(message)
        project_error.__cause__ = error
        return project_error
