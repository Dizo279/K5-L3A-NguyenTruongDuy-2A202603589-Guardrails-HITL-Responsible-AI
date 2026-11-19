import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def test_egress_policy_requires_exact_vinbank_https_endpoint():
    from assignment.pipeline import is_egress_allowed

    assert is_egress_allowed(
        "https://api.vinbank.example/v1/transfers", "approved transfer amount 500000"
    ) is True
    assert is_egress_allowed(
        "http://api.vinbank.example/v1/transfers", "approved transfer amount 500000"
    ) is False
    assert is_egress_allowed(
        "https://api.vinbank.example.evil.com/v1/transfers", "approved transfer amount 500000"
    ) is False


def test_egress_policy_rejects_sensitive_payloads():
    from assignment.pipeline import is_egress_allowed

    destination = "https://api.vinbank.example/v1/transfers"
    for payload in [
        "admin password is admin123",
        "API key is sk-vinbank-secret-2024",
        "database host is db.vinbank.internal",
        "contact 0901234567",
        "email user@example.com",
    ]:
        assert is_egress_allowed(destination, payload) is False


def test_pipeline_builders_return_ordered_plugins_and_observability():
    from assignment.audit_log import AuditLogPlugin
    from assignment.monitoring import MonitoringAlert
    from assignment.pipeline import build_observability, build_production_plugins
    from assignment.rate_limiter import RateLimitPlugin
    from guardrails.input_guardrails import InputGuardrailPlugin
    from guardrails.output_guardrails import OutputGuardrailPlugin

    plugins = build_production_plugins(max_requests=3, window_seconds=10)
    assert [type(plugin) for plugin in plugins] == [
        RateLimitPlugin,
        InputGuardrailPlugin,
        OutputGuardrailPlugin,
    ]
    assert plugins[0].max_requests == 3
    audit, monitor = build_observability()
    assert isinstance(audit, AuditLogPlugin)
    assert isinstance(monitor, MonitoringAlert)

