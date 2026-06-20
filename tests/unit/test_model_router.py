"""ModelRouter and schema validation unit tests."""

from __future__ import annotations

from loop_pilot.domain.models import RunRecord
from loop_pilot.domain.schema_validation import validate_run_record
from loop_pilot.domain.states import RunPhase
from loop_pilot.models.router import ModelRouter


def test_model_router_resolves_mock_roles() -> None:
    router = ModelRouter(
        {
            "roles": {"coding": {"adapter": "mock"}, "planning": {"adapter": "mock"}},
            "adapters": {"mock": {"kind": "mock"}},
        }
    )
    assert router.resolve("coding") == "mock"
    assert router.adapter_config("mock")["kind"] == "mock"


def test_model_router_blocks_coding_role_without_file_write_capability() -> None:
    router = ModelRouter(
        {
            "model_roles": {
                "coding_agent": {
                    "candidates": ["chat_api", "coding_cli"],
                    "require": {"file_write": True, "tool_calls": True, "dry_run": True},
                    "no_capable_adapter": "block",
                }
            },
            "adapters": {
                "chat_api": {
                    "kind": "api",
                    "capabilities": {
                        "supports_file_write": False,
                        "supports_tools": False,
                        "supports_dry_run": True,
                    },
                },
                "coding_cli": {
                    "kind": "cli",
                    "capabilities": {
                        "supports_file_write": True,
                        "supports_tools": True,
                        "supports_dry_run": True,
                    },
                },
            },
        },
        allow_real_adapters=True,
    )

    decision = router.resolve_role("coding_agent")

    assert decision.adapter_id == "coding_cli"
    assert "chat_api" in decision.excluded
    assert "file_write" in " ".join(decision.excluded["chat_api"])


def test_model_router_rejects_secret_and_sensitive_data_without_permission() -> None:
    router = ModelRouter(
        {
            "model_roles": {
                "analysis_medium": {
                    "candidates": ["api"],
                    "require": {"structured_output": True},
                    "no_capable_adapter": "block",
                }
            },
            "adapters": {
                "api": {
                    "kind": "api",
                    "capabilities": {"supports_structured_output": True},
                    "data_policy": {"max_data_class": "PROJECT"},
                }
            },
        }
    )

    assert router.resolve_role("analysis_medium", data_class="SECRET").blocked is True
    assert router.resolve_role("analysis_medium", data_class="SENSITIVE").blocked is True


def test_model_router_blocks_when_no_candidate_is_capable_even_for_deterministic_fallback() -> None:
    router = ModelRouter(
        {
            "model_roles": {
                "screening_economical": {
                    "candidates": ["cheap_api"],
                    "require": {"structured_output": True},
                    "no_capable_adapter": "deterministic_only",
                }
            },
            "adapters": {
                "cheap_api": {
                    "kind": "api",
                    "health": {"status": "unhealthy"},
                    "capabilities": {"supports_structured_output": True},
                }
            },
        },
        allow_real_adapters=True,
    )

    decision = router.resolve_role("screening_economical")

    assert decision.blocked is True
    assert decision.adapter_id is None
    assert decision.reason == "no_capable_adapter: deterministic_only"
    assert "unhealthy" in " ".join(decision.excluded["cheap_api"])


def test_model_router_filters_context_window_and_records_fallback() -> None:
    router = ModelRouter(
        {
            "model_roles": {
                "analysis_medium": {
                    "candidates": ["small_api", "large_api"],
                    "require": {"structured_output": True, "min_context_tokens": 8000},
                    "no_capable_adapter": "block",
                }
            },
            "adapters": {
                "small_api": {
                    "kind": "api",
                    "capabilities": {
                        "supports_structured_output": True,
                        "max_context_tokens": 4096,
                    },
                },
                "large_api": {
                    "kind": "api",
                    "capabilities": {
                        "supports_structured_output": True,
                        "max_context_tokens": 16000,
                    },
                },
            },
        },
        allow_real_adapters=True,
    )

    decision = router.resolve_role("analysis_medium")

    assert decision.adapter_id == "large_api"
    assert decision.fallback_used is True
    assert "context" in " ".join(decision.excluded["small_api"])


def test_run_record_validates_against_schema() -> None:
    record = RunRecord(run_id="golden-001", loop_type="intern", phase=RunPhase.TERMINATED)
    validate_run_record(record.to_dict())
