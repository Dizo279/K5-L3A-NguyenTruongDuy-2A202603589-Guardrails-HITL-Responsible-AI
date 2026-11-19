import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def test_hitl_decision_points_are_complete_and_actionable():
    from hitl.hitl import hitl_decision_points

    required = {
        "name",
        "trigger",
        "hitl_model",
        "context_needed",
        "example",
        "approval_path",
        "audit_fields",
    }
    assert len(hitl_decision_points) == 3
    for point in hitl_decision_points:
        assert required.issubset(point)
        assert all(point[field] and "TODO" not in point[field] for field in required)

