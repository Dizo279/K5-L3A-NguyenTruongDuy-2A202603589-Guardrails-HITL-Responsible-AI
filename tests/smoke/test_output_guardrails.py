import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def test_content_filter_redacts_sensitive_categories():
    from guardrails.output_guardrails import content_filter

    result = content_filter(
        "Password: admin123; API key: sk-secret-123; "
        "phone 0901234567; email user@example.com; CCCD 123456789012"
    )

    assert result["safe"] is False
    assert len(result["issues"]) >= 5
    assert "admin123" not in result["redacted"]
    assert "sk-secret-123" not in result["redacted"]
    assert "user@example.com" not in result["redacted"]


def test_output_guardrail_plugin_redacts_model_content():
    from google.genai import types
    from guardrails.output_guardrails import OutputGuardrailPlugin

    response = type(
        "Response",
        (),
        {
            "content": types.Content(
                role="model",
                parts=[types.Part.from_text(text="Your password: admin123")],
            )
        },
    )()

    async def exercise():
        plugin = OutputGuardrailPlugin(use_llm_judge=False)
        result = await plugin.after_model_callback(
            callback_context=None,
            llm_response=response,
        )
        return plugin, result

    plugin, result = asyncio.run(exercise())
    text = result.content.parts[0].text
    assert "admin123" not in text
    assert "[REDACTED]" in text
    assert plugin.total_count == 1
    assert plugin.redacted_count == 1


def test_output_guardrail_plugin_leaves_safe_content_unchanged():
    from google.genai import types
    from guardrails.output_guardrails import OutputGuardrailPlugin

    response = type(
        "Response",
        (),
        {
            "content": types.Content(
                role="model",
                parts=[types.Part.from_text(text="Your savings rate is 4.25%.")],
            )
        },
    )()

    async def exercise():
        plugin = OutputGuardrailPlugin(use_llm_judge=False)
        return plugin, await plugin.after_model_callback(
            callback_context=None, llm_response=response
        )

    plugin, result = asyncio.run(exercise())
    assert result.content.parts[0].text == "Your savings rate is 4.25%."
    assert plugin.redacted_count == 0

