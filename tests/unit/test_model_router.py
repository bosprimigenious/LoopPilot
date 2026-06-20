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


def test_run_record_validates_against_schema() -> None:
    record = RunRecord(run_id="golden-001", loop_type="intern", phase=RunPhase.TERMINATED)
    validate_run_record(record.to_dict())
