import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def test_red_openrouter_configuration(monkeypatch):
    monkeypatch.setenv("RED_TEAM_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "router-test-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    from core.config import get_red_model, get_red_provider, red_openai_client_kwargs

    assert get_red_provider() == "openrouter"
    assert get_red_model() == "openai/gpt-4o-mini"
    assert red_openai_client_kwargs() == {
        "api_key": "router-test-key",
        "base_url": "https://openrouter.ai/api/v1",
    }


def test_nemo_openrouter_model_entry_uses_router_key_and_endpoint():
    from agents.red_advance_nemo import _model_entry

    entry = _model_entry("openrouter", "openai/gpt-4o-mini")
    assert entry["engine"] == "openai"
    assert entry["api_key_env_var"] == "OPENROUTER_API_KEY"
    assert entry["parameters"]["base_url"] == "https://openrouter.ai/api/v1"

