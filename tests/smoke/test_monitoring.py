import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def test_monitoring_emits_alerts_for_exceeded_thresholds():
    from assignment.monitoring import MonitoringAlert

    monitor = MonitoringAlert(
        block_rate_threshold=0.5,
        rate_limit_hit_threshold=1,
        judge_fail_rate_threshold=0.25,
    )
    monitor.total_requests = 4
    monitor.blocked_requests = 3
    monitor.rate_limit_hits = 2
    monitor.judge_checks = 4
    monitor.judge_fails = 2

    alerts = monitor.check_metrics()

    assert {alert.metric for alert in alerts} == {
        "block_rate",
        "rate_limit_hits",
        "judge_fail_rate",
    }
    assert monitor.snapshot()["block_rate"] == 0.75
    assert monitor.snapshot()["judge_fail_rate"] == 0.5


def test_monitoring_does_not_alert_at_or_below_threshold_and_exports():
    from assignment.monitoring import MonitoringAlert

    monitor = MonitoringAlert()
    monitor.total_requests = 2
    monitor.blocked_requests = 1
    monitor.rate_limit_hits = 5
    monitor.judge_checks = 2
    monitor.judge_fails = 0
    assert monitor.check_metrics() == []

    output = ROOT / "outputs" / "test-monitoring" / "metrics.json"
    try:
        path = monitor.export_json(str(output))
        assert path == str(output)
        data = json.loads(output.read_text(encoding="utf-8"))
        assert data["total_requests"] == 2
        assert data["block_rate"] == 0.5
    finally:
        output.unlink(missing_ok=True)
        output.parent.rmdir()
        output.parent.parent.rmdir()


def test_monitoring_empty_snapshot_has_zero_rates():
    from assignment.monitoring import MonitoringAlert

    snapshot = MonitoringAlert().snapshot()
    assert snapshot["block_rate"] == 0.0
    assert snapshot["judge_fail_rate"] == 0.0

