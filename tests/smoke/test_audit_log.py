import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def test_audit_log_records_input_output_and_latency(monkeypatch):
    from assignment.audit_log import AuditLogPlugin

    timestamps = iter(["2026-11-19T10:00:00+00:00", "2026-11-19T10:00:01+00:00"])
    monkeypatch.setattr("assignment.audit_log.utc_now_iso", lambda: next(timestamps))
    plugin = AuditLogPlugin()

    plugin.record_input(user_id="alice", text="What is my balance?", request_id="r1")
    plugin.record_output(
        user_id="alice",
        text="Your balance is ...",
        blocked=False,
        layer="model",
        request_id="r1",
    )

    assert len(plugin.logs) == 1
    entry = plugin.logs[0]
    assert entry["request_id"] == "r1"
    assert entry["user_id"] == "alice"
    assert entry["input"] == "What is my balance?"
    assert entry["output"] == "Your balance is ..."
    assert entry["blocked"] is False
    assert entry["layer"] == "model"
    assert entry["started_at"] == "2026-11-19T10:00:00+00:00"
    assert entry["completed_at"] == "2026-11-19T10:00:01+00:00"
    assert entry["latency_ms"] == 1000.0


def test_audit_log_exports_json_and_creates_parent_directory():
    from assignment.audit_log import AuditLogPlugin

    plugin = AuditLogPlugin()
    plugin.record_input(user_id="bob", text="Hello", request_id="r2")
    output = ROOT / "outputs" / "test-audit-log" / "audit.json"
    try:
        path = plugin.export_json(str(output))
        assert path == str(output)
        assert json.loads(output.read_text(encoding="utf-8"))[0]["input"] == "Hello"
    finally:
        output.unlink(missing_ok=True)
        output.parent.rmdir()
        output.parent.parent.rmdir()

