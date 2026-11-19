"""
Assignment 11 — Audit Log starter (TODO).

Records every interaction for forensics. Never blocks by itself —
other layers catch attacks; this layer makes them reviewable.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def default_audit_log_path() -> str:
    """Always resolve to <repo>/outputs/… (safe when cwd is src/)."""
    repo_root = Path(__file__).resolve().parents[2]
    return str(repo_root / "outputs" / "audit_log.json")


class AuditLogPlugin:
    """Framework-agnostic audit logger (wire into ADK callbacks or your pipeline)."""

    def __init__(self):
        self.name = "audit_log"
        self.logs: list[dict] = []
        self._open: dict[str, float] = {}

    def record_input(self, *, user_id: str, text: str, request_id: str | None = None):
        """Store an interaction's input until its output is available."""
        key = request_id or user_id
        started_at = utc_now_iso()
        entry = {
            "request_id": request_id,
            "user_id": user_id,
            "input": text,
            "started_at": started_at,
        }
        self.logs.append(entry)
        self._open[key] = len(self.logs) - 1

    def record_output(
        self,
        *,
        user_id: str,
        text: str,
        blocked: bool = False,
        layer: str | None = None,
        request_id: str | None = None,
    ):
        """Complete and append an interaction log entry."""
        key = request_id or user_id
        index = self._open.pop(key, None)
        if index is None:
            self.logs.append({
                "request_id": request_id,
                "user_id": user_id,
                "input": None,
                "started_at": None,
            })
            index = len(self.logs) - 1
        started = self.logs[index]
        completed_at = utc_now_iso()
        latency_ms = None
        if started["started_at"]:
            start = datetime.fromisoformat(started["started_at"])
            end = datetime.fromisoformat(completed_at)
            latency_ms = (end - start).total_seconds() * 1000

        started.update(
            output=text,
            blocked=blocked,
            layer=layer,
            completed_at=completed_at,
            latency_ms=latency_ms,
        )

    def export_json(self, filepath: str | None = None):
        """Write logs to disk (JSON array) under repo-root ``outputs/`` by default."""
        path = Path(filepath or default_audit_log_path())
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.logs, indent=2), encoding="utf-8")
        return str(path)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
