"""Backward-compatible re-exports for APIModelAdapter."""

from loop_pilot.adapters.openai_compatible import (
    OpenAICompatibleAdapter as APIModelAdapter,
    OpenAICompatibleConfig as APIModelConfig,
)

__all__ = ["APIModelAdapter", "APIModelConfig"]
