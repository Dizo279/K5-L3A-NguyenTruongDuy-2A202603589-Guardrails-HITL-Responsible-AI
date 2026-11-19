"""Blue Team uses Liquid's direct OpenAI-compatible endpoint."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def test_blue_configuration_targets_liquid(monkeypatch):
    monkeypatch.setenv("LIQUID_API_KEY", "liquid-test-key")

    from core.config import (
        LIQUID_BASE_URL,
        LIQUID_MODEL,
        get_blue_model,
        get_blue_provider,
        liquid_client_kwargs,
    )

    assert get_blue_provider() == "liquid"
    assert get_blue_model() == "lfm3-1.7b"
    assert LIQUID_MODEL == "lfm3-1.7b"
    assert LIQUID_BASE_URL == "https://api.liquid.ai/openai/v1"
    assert liquid_client_kwargs() == {
        "api_key": "liquid-test-key",
        "base_url": "https://api.liquid.ai/openai/v1",
    }


def test_blue_factory_uses_liquid_configuration(monkeypatch):
    monkeypatch.setenv("LIQUID_API_KEY", "liquid-test-key")

    from core.openai_runtime import create_blue_pair

    _, runner = create_blue_pair(
        name="blue",
        instruction="Be helpful.",
        app_name="test",
    )

    assert runner.provider == "liquid"
    assert runner.model == "lfm3-1.7b"
    assert runner.client_kwargs["base_url"] == "https://api.liquid.ai/openai/v1"

