import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def test_adversarial_prompts_are_actionable_and_not_placeholders():
    from attacks.attacks import adversarial_prompts

    assert len(adversarial_prompts) >= 5
    for attack in adversarial_prompts[:5]:
        assert attack["input"]
        assert "TODO" not in attack["input"]
        assert len(attack["input"]) >= 40

