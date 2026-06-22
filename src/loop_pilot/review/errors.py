"""Review decision errors (0.4-c)."""

from __future__ import annotations


class ReviewDecisionError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
