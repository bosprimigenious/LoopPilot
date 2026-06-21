"""Configuration loading and validation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from loop_pilot.domain.errors import ErrorCode, LoopPilotError


@dataclass
class LoopPilotConfig:
    runtime: dict[str, Any] = field(default_factory=dict)
    reporting: dict[str, Any] = field(default_factory=dict)
    workspaces: dict[str, Any] = field(default_factory=dict)
    intern: dict[str, Any] = field(default_factory=dict)
    paper: dict[str, Any] = field(default_factory=dict)
    daily_news: dict[str, Any] = field(default_factory=dict)
    policies: dict[str, Any] = field(default_factory=dict)
    sources: dict[str, Any] = field(default_factory=dict)
    models: dict[str, Any] = field(default_factory=dict)
    adapters: dict[str, Any] = field(default_factory=dict)
    config_dir: Path = field(default_factory=lambda: Path("config"))

    @property
    def state_dir(self) -> Path:
        return Path(self.runtime.get("state_dir", "var/state"))

    @property
    def artifact_dir(self) -> Path:
        return Path(self.runtime.get("artifact_dir", "var/artifacts"))

    @property
    def sqlite_path(self) -> Path:
        return Path(
            self.runtime.get(
                "sqlite_path",
                self.state_dir / "loop_pilot.db",
            )
        )

    @property
    def lock_dir(self) -> Path:
        return Path(self.runtime.get("lock_dir", self.state_dir / "locks"))

    @property
    def allow_real_adapters(self) -> bool:
        return bool(self.runtime.get("allow_real_adapters", False))

    @property
    def dry_run(self) -> bool:
        return bool(self.runtime.get("dry_run", False))

    def get_source_profile(self, profile: str) -> dict[str, Any]:
        profiles = self.sources.get("profiles", {})
        if profile not in profiles:
            raise LoopPilotError(
                code=ErrorCode.CONFIG_INVALID,
                component="config.sources",
                message=f"Unknown source profile: {profile}",
            )
        cfg = profiles[profile]
        return cfg if isinstance(cfg, dict) else {}

    def snapshot_hash(self) -> str:
        payload = {
            "runtime": self.runtime,
            "workspaces": self.workspaces,
            "intern": self.intern,
            "paper": self.paper,
            "daily_news": self.daily_news,
        }
        canonical = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def load_config(config_dir: Path | None = None) -> LoopPilotConfig:
    config_dir = config_dir or Path("config")
    if not config_dir.exists():
        raise LoopPilotError(
            code=ErrorCode.CONFIG_INVALID,
            component="config",
            message=f"Config directory not found: {config_dir}",
        )

    main = _load_yaml(config_dir / "loop-pilot.yaml")
    runtime = main.get("runtime", {})
    reporting = main.get("reporting", {})

    forbidden_keys = {"password", "api_key", "secret", "token"}
    for fname in config_dir.glob("*.yaml"):
        text = fname.read_text(encoding="utf-8").lower()
        for key in forbidden_keys:
            if f"{key}:" in text and "auth_env" not in text:
                raise LoopPilotError(
                    code=ErrorCode.CONFIG_INVALID,
                    component="config",
                    message=f"Plaintext secret-like key in {fname.name}",
                )

    return LoopPilotConfig(
        runtime=runtime,
        reporting=reporting,
        workspaces=main.get("workspaces", {}),
        intern=_load_yaml(config_dir / "intern.yaml"),
        paper=_load_yaml(config_dir / "paper.yaml"),
        daily_news=_load_yaml(config_dir / "daily_news.yaml"),
        policies=_load_yaml(config_dir / "policies.yaml"),
        sources=_load_yaml(config_dir / "sources.yaml"),
        models=_merge_models_config(config_dir),
        adapters=_load_yaml(config_dir / "adapters.yaml"),
        config_dir=config_dir,
    )


def _merge_models_config(config_dir: Path) -> dict[str, Any]:
    models = _load_yaml(config_dir / "models.yaml")
    adapters_file = _load_yaml(config_dir / "adapters.yaml")
    file_adapters = adapters_file.get("adapters", {})
    if file_adapters:
        merged = dict(models.get("adapters", {}))
        merged.update(file_adapters)
        models["adapters"] = merged
    return models


def default_config_dict() -> dict[str, Any]:
    return {
        "runtime": {
            "timezone": "Asia/Shanghai",
            "state_backend": "json",
            "state_dir": "var/state",
            "artifact_dir": "var/artifacts",
            "checkpoint_dir": "var/checkpoints",
            "execution_mode": "sequential",
            "dry_run": False,
            "max_concurrent_runs": 1,
            "allow_real_adapters": False,
        },
        "reporting": {
            "format": "markdown",
            "include_evidence_links": True,
            "redact_sensitive_values": True,
        },
    }
