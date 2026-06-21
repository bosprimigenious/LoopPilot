"""SQLite database operations for 0.4-a state reliability."""

from __future__ import annotations

import shutil
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from loop_pilot.storage.migrations import (
    CURRENT_SCHEMA_VERSION,
    apply_migrations,
    get_applied_versions,
    get_current_schema_version,
    plan_migrations,
    required_tables,
)


@dataclass
class DbStatus:
    backend: str
    db_path: Path | None
    exists: bool
    schema_version: int
    target_schema_version: int
    pending_migrations: list[int]
    run_count: int
    active_run_count: int
    lock_dir: Path
    lock_files: list[str] = field(default_factory=list)


@dataclass
class VerifyIssue:
    severity: str  # error | warning
    code: str
    message: str


@dataclass
class VerifyReport:
    ok: bool
    issues: list[VerifyIssue] = field(default_factory=list)


@dataclass
class BackupPlan:
    sources: list[tuple[Path, Path]]
    dry_run: bool


def connect_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_db_status(
    *,
    backend: str,
    db_path: Path | None,
    lock_dir: Path,
) -> DbStatus:
    lock_files = sorted(path.name for path in lock_dir.glob("*.lock")) if lock_dir.exists() else []

    if backend != "sqlite" or db_path is None:
        return DbStatus(
            backend=backend,
            db_path=db_path,
            exists=False,
            schema_version=0,
            target_schema_version=CURRENT_SCHEMA_VERSION,
            pending_migrations=[],
            run_count=0,
            active_run_count=0,
            lock_dir=lock_dir,
            lock_files=lock_files,
        )

    exists = db_path.exists()
    schema_version = 0
    pending: list[int] = list(range(1, CURRENT_SCHEMA_VERSION + 1)) if not exists else []
    run_count = 0
    active_run_count = 0

    if exists:
        with connect_db(db_path) as conn:
            schema_version = get_current_schema_version(conn)
            pending = plan_migrations(conn)
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            if "runs" in tables:
                run_count = int(conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0])
                active_run_count = int(
                    conn.execute(
                        "SELECT COUNT(*) FROM runs WHERE phase != 'TERMINATED' OR outcome IS NULL"
                    ).fetchone()[0]
                )

    return DbStatus(
        backend=backend,
        db_path=db_path,
        exists=exists,
        schema_version=schema_version,
        target_schema_version=CURRENT_SCHEMA_VERSION,
        pending_migrations=pending,
        run_count=run_count,
        active_run_count=active_run_count,
        lock_dir=lock_dir,
        lock_files=lock_files,
    )


def migrate_database(db_path: Path, *, dry_run: bool = False) -> list[int]:
    with connect_db(db_path) as conn:
        return apply_migrations(conn, dry_run=dry_run)


def verify_database(db_path: Path, artifact_dir: Path) -> VerifyReport:
    issues: list[VerifyIssue] = []

    if not db_path.exists():
        issues.append(
            VerifyIssue(
                severity="error",
                code="db_missing",
                message=f"SQLite database not found: {db_path}",
            )
        )
        return VerifyReport(ok=False, issues=issues)

    with connect_db(db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        for table in required_tables():
            if table not in tables:
                issues.append(
                    VerifyIssue(
                        severity="error",
                        code="missing_table",
                        message=f"Missing required table: {table}",
                    )
                )

        orphan_checkpoints = conn.execute(
            """
            SELECT checkpoint_id, run_id FROM checkpoints
            WHERE run_id NOT IN (SELECT run_id FROM runs)
            """
        ).fetchall()
        for row in orphan_checkpoints:
            issues.append(
                VerifyIssue(
                    severity="error",
                    code="orphan_checkpoint",
                    message=f"Checkpoint {row['checkpoint_id']} references missing run {row['run_id']}",
                )
            )

        orphan_manifests = conn.execute(
            """
            SELECT run_id FROM artifact_manifests
            WHERE run_id NOT IN (SELECT run_id FROM runs)
            """
        ).fetchall()
        for row in orphan_manifests:
            issues.append(
                VerifyIssue(
                    severity="warning",
                    code="orphan_manifest",
                    message=f"Artifact manifest for missing run {row['run_id']}",
                )
            )

        half_terminal = conn.execute(
            """
            SELECT run_id, phase, outcome FROM runs
            WHERE phase = 'TERMINATED' AND outcome IS NULL
            """
        ).fetchall()
        for row in half_terminal:
            issues.append(
                VerifyIssue(
                    severity="error",
                    code="half_terminal",
                    message=f"Run {row['run_id']} is TERMINATED without outcome",
                )
            )

        inconsistent = conn.execute(
            """
            SELECT run_id, phase, outcome FROM runs
            WHERE phase != 'TERMINATED' AND outcome IS NOT NULL
              AND outcome NOT IN ('cancelled')
            """
        ).fetchall()
        for row in inconsistent:
            issues.append(
                VerifyIssue(
                    severity="warning",
                    code="inconsistent_state",
                    message=(
                        f"Run {row['run_id']} has phase={row['phase']} "
                        f"with outcome={row['outcome']}"
                    ),
                )
            )

        for row in conn.execute("SELECT run_id, payload FROM artifact_manifests").fetchall():
            run_id = row["run_id"]
            manifest_path = _artifact_manifest_path(artifact_dir, run_id, row["payload"])
            if manifest_path is not None and not manifest_path.exists():
                issues.append(
                    VerifyIssue(
                        severity="warning",
                        code="manifest_missing_on_disk",
                        message=f"On-disk manifest missing for run {run_id}: {manifest_path}",
                    )
                )

        for row in conn.execute(
            "SELECT run_id, loop_type FROM runs WHERE phase != 'TERMINATED'"
        ).fetchall():
            run_id = row["run_id"]
            loop_type = row["loop_type"]
            run_dir = _run_artifact_dir(artifact_dir, loop_type, run_id)
            if run_dir.exists():
                tool_results = run_dir / "tool-results.json"
                trace = run_dir / "trace.jsonl"
                if not tool_results.exists() and trace.exists():
                    issues.append(
                        VerifyIssue(
                            severity="warning",
                            code="tool_results_missing",
                            message=f"tool-results.json missing for active run {run_id}",
                        )
                    )

    has_errors = any(issue.severity == "error" for issue in issues)
    return VerifyReport(ok=not has_errors, issues=issues)


def plan_backup(
    *,
    db_path: Path,
    state_dir: Path,
    config_dir: Path,
    backup_dir: Path,
    dry_run: bool,
) -> BackupPlan:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    target_root = _unique_backup_root(backup_dir, stamp)
    sources: list[tuple[Path, Path]] = []

    for source in (db_path, state_dir, config_dir):
        if source.exists():
            sources.append((source, target_root / source.name))

    return BackupPlan(sources=sources, dry_run=dry_run)


def _unique_backup_root(backup_dir: Path, stamp: str) -> Path:
    candidate = backup_dir / stamp
    if not candidate.exists():
        return candidate
    suffix = 1
    while True:
        alternate = backup_dir / f"{stamp}-{suffix:03d}"
        if not alternate.exists():
            return alternate
        suffix += 1


def execute_backup(plan: BackupPlan) -> Path | None:
    if not plan.sources:
        return None

    target_root = plan.sources[0][1].parent
    if plan.dry_run:
        return target_root

    target_root.mkdir(parents=True, exist_ok=True)
    for source, destination in plan.sources:
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    return target_root


def _run_artifact_dir(artifact_dir: Path, loop_type: str, run_id: str) -> Path:
    segment = loop_type.replace("_", "-")
    return artifact_dir / segment / run_id


def _artifact_manifest_path(artifact_dir: Path, run_id: str, payload: str) -> Path | None:
    import json

    try:
        manifest = json.loads(payload)
    except json.JSONDecodeError:
        return None

    run_dir = manifest.get("run_dir")
    if isinstance(run_dir, str):
        return artifact_dir.parent / run_dir / "artifact-manifest.json"

    loop_type = manifest.get("loop_type")
    if isinstance(loop_type, str):
        return _run_artifact_dir(artifact_dir, loop_type, run_id) / "artifact-manifest.json"

    return _run_artifact_dir(artifact_dir, "intern", run_id) / "artifact-manifest.json"


def sqlite_doctor_checks(db_path: Path, lock_dir: Path) -> list[str]:
    issues: list[str] = []
    warnings: list[str] = []

    if not lock_dir.exists():
        try:
            lock_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            issues.append(f"lock_dir not writable: {lock_dir} ({exc})")

    if db_path.parent.exists():
        test_file = db_path.parent / ".write_test"
        try:
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink(missing_ok=True)
        except OSError as exc:
            issues.append(f"sqlite_path parent not writable: {db_path.parent} ({exc})")

    if db_path.exists():
        try:
            with connect_db(db_path) as conn:
                conn.execute("SELECT 1")
                applied = get_applied_versions(conn)
                if applied and max(applied) < CURRENT_SCHEMA_VERSION:
                    warnings.append(
                        f"schema behind target ({max(applied)} < {CURRENT_SCHEMA_VERSION}); "
                        "run: loop-pilot db migrate"
                    )
        except sqlite3.Error as exc:
            issues.append(f"sqlite not readable: {db_path} ({exc})")

    stale_locks = list(lock_dir.glob("*.lock")) if lock_dir.exists() else []
    if stale_locks:
        warnings.append(f"{len(stale_locks)} lock file(s) present in {lock_dir}")

    return issues + [f"Warning: {item}" for item in warnings]
