"""OpenAI-compatible API Adapter with injectable HTTP client for tests."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from loop_pilot.adapters.base import (
    AdapterCapabilities,
    AdapterRequest,
    AdapterResult,
    AdapterStatus,
    BaseAdapter,
    HealthStatus,
)
from loop_pilot.domain.errors import ErrorCode, LoopPilotError
from loop_pilot.domain.models import ArtifactReference, content_hash
from loop_pilot.runtime.boundaries import CancellationToken

HttpClient = Callable[[dict[str, Any], dict[str, str]], dict[str, Any]]


@dataclass(frozen=True)
class OpenAICompatibleConfig:
    provider: str
    endpoint: str
    model: str
    auth_env: str | None = None
    timeout_seconds: int = 60


class OpenAICompatibleAdapter(BaseAdapter):
    """HTTP chat-completions adapter; API keys read from env only."""

    def __init__(
        self,
        adapter_id: str,
        endpoint: str,
        model: str,
        auth_env: str | None,
        artifact_dir: Path,
        http_client: HttpClient | None = None,
        provider: str = "openai_compatible",
        timeout_seconds: int = 60,
    ) -> None:
        self.adapter_id = adapter_id
        self.provider = provider
        self.endpoint = endpoint
        self.model = model
        self.auth_env = auth_env
        self.artifact_dir = artifact_dir
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.http_client = http_client or self._default_http_client
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_config(
        cls,
        adapter_id: str,
        config: OpenAICompatibleConfig | dict[str, Any],
        artifact_dir: Path,
        http_client: HttpClient | None = None,
    ) -> OpenAICompatibleAdapter:
        if isinstance(config, dict):
            config = OpenAICompatibleConfig(
                provider=str(config.get("provider", "openai_compatible")),
                endpoint=str(config["endpoint"]),
                model=str(config["model"]),
                auth_env=config.get("auth_env"),
                timeout_seconds=int(config.get("timeout_seconds", 60)),
            )
        return cls(
            adapter_id=adapter_id,
            endpoint=config.endpoint,
            model=config.model,
            auth_env=config.auth_env,
            artifact_dir=artifact_dir,
            http_client=http_client,
            provider=config.provider,
            timeout_seconds=config.timeout_seconds,
        )

    def safe_config(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "endpoint": self.endpoint,
            "model": self.model,
            "auth_env": self.auth_env,
        }

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            supports_structured_output=True,
            supports_dry_run=True,
            network_required=True,
        )

    def healthcheck(self) -> HealthStatus:
        return HealthStatus(status="configured", adapter_id=self.adapter_id)

    def execute(
        self,
        request: dict[str, Any] | AdapterRequest,
        timeout: float | None = None,
        cancellation: CancellationToken | None = None,
    ) -> AdapterResult:
        if isinstance(request, AdapterRequest):
            payload = request.to_dict()
        else:
            payload = dict(request)
        start = time.monotonic()
        if cancellation and cancellation.is_cancelled:
            return self._error(AdapterStatus.CANCELLED.value, ErrorCode.MODEL_TIMEOUT, start)

        token = os.environ.get(self.auth_env or "") if self.auth_env else None
        if self.auth_env and not token:
            return self._error(AdapterStatus.ERROR.value, ErrorCode.CONFIG_INVALID, start)

        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer <redacted>"

        api_payload = {
            "model": self.model,
            "messages": payload.get("messages", []),
            "response_format": {"type": "json_object"},
            "timeout": timeout or self.timeout_seconds,
        }

        try:
            response = self.http_client(api_payload, self._auth_headers(token))
            structured = self._extract_structured_output(response)
        except json.JSONDecodeError as exc:
            artifact = self._write_artifact("schema-error.txt", str(exc))
            return self._error(
                AdapterStatus.ERROR.value,
                ErrorCode.MODEL_OUTPUT_INVALID,
                start,
                stderr_artifact=artifact,
            )
        except urllib.error.HTTPError as exc:
            code = ErrorCode.MODEL_RATE_LIMIT if exc.code in {429, 500, 502, 503} else ErrorCode.CONFIG_INVALID
            return self._error(AdapterStatus.ERROR.value, code, start)
        except Exception as exc:  # noqa: BLE001
            artifact = self._write_artifact("api-error.txt", self._redact(str(exc)))
            return self._error(
                AdapterStatus.ERROR.value,
                ErrorCode.MODEL_OUTPUT_INVALID,
                start,
                stderr_artifact=artifact,
            )

        transcript = self._write_artifact(
            "transcript.json",
            json.dumps(self._redact_response(response), sort_keys=True),
        )
        usage = response.get("usage", {}) if isinstance(response, dict) else {}
        usage["duration_ms"] = int((time.monotonic() - start) * 1000)
        return AdapterResult(
            status=AdapterStatus.SUCCESS.value,
            structured_output=structured,
            transcript_artifact=transcript,
            usage=usage,
        )

    def estimate_cost(self, _request: dict[str, Any] | AdapterRequest) -> dict[str, Any]:
        return {"cost": None}

    def normalize_error(self, error: Exception) -> LoopPilotError:
        return LoopPilotError(
            code=ErrorCode.MODEL_OUTPUT_INVALID,
            component=self.adapter_id,
            message=str(error),
            retryable=False,
        )

    def _auth_headers(self, token: str | None) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _extract_structured_output(self, response: dict[str, Any]) -> dict[str, Any]:
        choices = response.get("choices", [])
        if not choices:
            raise json.JSONDecodeError("missing choices", "", 0)
        content = choices[0].get("message", {}).get("content")
        if isinstance(content, dict):
            return content
        if not isinstance(content, str):
            raise json.JSONDecodeError("missing content", "", 0)
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise json.JSONDecodeError("content is not object", content, 0)
        return parsed

    def _default_http_client(self, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        body = json.dumps(payload).encode()
        req = urllib.request.Request(self.endpoint, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=payload.get("timeout")) as response:  # noqa: S310
            return json.loads(response.read().decode())

    def _error(
        self,
        status: str,
        code: ErrorCode,
        start: float,
        stderr_artifact: ArtifactReference | None = None,
    ) -> AdapterResult:
        return AdapterResult(
            status=status,
            stderr_artifact=stderr_artifact,
            usage={"duration_ms": int((time.monotonic() - start) * 1000)},
            error_code=code.value,
        )

    def _write_artifact(self, name: str, content: str) -> ArtifactReference:
        path = self.artifact_dir / f"{self.adapter_id}-{name}"
        path.write_text(content, encoding="utf-8")
        rel = path.relative_to(self.artifact_dir)
        return ArtifactReference(
            artifact_id=f"{self.adapter_id}-{name}",
            kind="transcript",
            path=str(rel),
            media_type="text/plain",
            sha256=content_hash({"content": content}),
            size_bytes=len(content.encode()),
            created_by=self.adapter_id,
        )

    @staticmethod
    def _redact(text: str) -> str:
        import re

        redacted = re.sub(r"Bearer\s+\S+", "Bearer <redacted>", text, flags=re.IGNORECASE)
        return redacted.replace("Bearer ", "Bearer <redacted> ")

    def _redact_response(self, response: dict[str, Any]) -> dict[str, Any]:
        import re

        raw = json.dumps(response)
        raw = re.sub(r"sk-[A-Za-z0-9_-]+", "<redacted>", raw)
        raw = re.sub(r"Bearer\s+[A-Za-z0-9_-]+", "Bearer <redacted>", raw, flags=re.IGNORECASE)
        return json.loads(raw)
