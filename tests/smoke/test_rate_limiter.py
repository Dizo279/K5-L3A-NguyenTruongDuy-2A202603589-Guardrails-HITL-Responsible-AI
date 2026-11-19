import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def run(callback, user_id):
    return asyncio.run(
        callback(
            invocation_context=type("Context", (), {"user_id": user_id})(),
            user_message=None,
        )
    )


def test_rate_limiter_allows_limit_then_blocks_next_request(monkeypatch):
    from assignment.rate_limiter import RateLimitPlugin

    clock = iter([100.0, 101.0, 102.0])
    monkeypatch.setattr("assignment.rate_limiter.time.time", lambda: next(clock))
    plugin = RateLimitPlugin(max_requests=2, window_seconds=60)

    assert run(plugin.on_user_message_callback, "alice") is None
    assert run(plugin.on_user_message_callback, "alice") is None
    blocked = run(plugin.on_user_message_callback, "alice")

    assert blocked is not None
    assert "Rate limit exceeded" in blocked.parts[0].text
    assert plugin.total_count == 3
    assert plugin.blocked_count == 1


def test_rate_limiter_expires_old_requests_and_is_per_user(monkeypatch):
    from assignment.rate_limiter import RateLimitPlugin

    now = [100.0]
    monkeypatch.setattr("assignment.rate_limiter.time.time", lambda: now[0])
    plugin = RateLimitPlugin(max_requests=1, window_seconds=10)

    assert run(plugin.on_user_message_callback, "alice") is None
    assert run(plugin.on_user_message_callback, "bob") is None
    assert run(plugin.on_user_message_callback, "alice") is not None

    now[0] = 110.0
    assert run(plugin.on_user_message_callback, "alice") is None

