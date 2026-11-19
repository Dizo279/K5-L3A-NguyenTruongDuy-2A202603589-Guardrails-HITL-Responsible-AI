import json
import sys
from pathlib import Path

import asyncio

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def test_assignment_suite_returns_contract_and_writes_outputs():
    from assignment.pipeline import build_observability, run_assignment_suite

    async def fake_chat(text):
        return "VinBank response: safe banking information."

    audit, monitor = build_observability()
    output_dir = ROOT / "outputs" / "test-assignment-suite"
    result = asyncio.run(run_assignment_suite({
        "chat": fake_chat,
        "audit": audit,
        "monitor": monitor,
        "output_dir": output_dir,
    }))

    assert result["framework"] == "google-adk"
    assert len(result["safe_queries"]) >= 5
    assert len(result["attack_queries"]) >= 7
    assert sum(row["blocked"] for row in result["attack_queries"]) >= 5
    assert result["rate_limit"]["blocked"] >= 1
    assert result["rate_limit"]["passed"] + result["rate_limit"]["blocked"] == result["rate_limit"]["sent"]
    assert len(result["edge_cases"]) >= 3
    assert (output_dir / "results.json").is_file()
    assert (output_dir / "audit_log.json").is_file()
    assert (output_dir / "metrics.json").is_file()
    assert json.loads((output_dir / "results.json").read_text(encoding="utf-8"))["framework"] == "google-adk"
    for path in output_dir.iterdir():
        path.unlink()
    output_dir.rmdir()

