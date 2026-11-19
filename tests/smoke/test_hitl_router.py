import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def test_confidence_router_uses_confidence_bands():
    from hitl.hitl import ConfidenceRouter

    router = ConfidenceRouter()
    high = router.route("balance", 0.95)
    medium = router.route("ambiguous", 0.8)
    low = router.route("uncertain", 0.4)

    assert (high.action, high.priority, high.requires_human) == ("auto_send", "low", False)
    assert (medium.action, medium.priority, medium.requires_human) == ("queue_review", "normal", True)
    assert (low.action, low.priority, low.requires_human) == ("escalate", "high", True)


def test_confidence_router_always_escalates_high_risk_actions():
    from hitl.hitl import ConfidenceRouter

    decision = ConfidenceRouter().route("transfer", 0.99, "transfer_money")
    assert decision.action == "escalate"
    assert decision.priority == "high"
    assert decision.requires_human is True
    assert "transfer_money" in decision.reason

