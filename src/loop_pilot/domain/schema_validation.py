"""Validate structured outputs against JSON Schemas."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from loop_pilot.domain.errors import ErrorCode, LoopPilotError

SCHEMA_DIR = Path(__file__).resolve().parents[3] / "schemas"


def validate_against_schema(payload: dict, schema_name: str) -> None:
    schema_path = SCHEMA_DIR / schema_name
    if not schema_path.exists():
        raise LoopPilotError(
            code=ErrorCode.CONFIG_INVALID,
            component="schema",
            message=f"Schema not found: {schema_name}",
        )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError as exc:
        raise LoopPilotError(
            code=ErrorCode.MODEL_OUTPUT_INVALID,
            component="schema",
            message=str(exc.message),
            retryable=True,
        ) from exc


def validate_run_record(record_dict: dict) -> None:
    validate_against_schema(record_dict, "run-record.json")


def validate_artifact_manifest(manifest_dict: dict) -> None:
    validate_against_schema(manifest_dict, "artifact-manifest.json")
