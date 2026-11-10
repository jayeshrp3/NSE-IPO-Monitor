import json
from pathlib import Path


def test_every_functional_requirement_maps_to_implementation_and_evaluation():
    traceability = json.loads(Path("evaluation/traceability.json").read_text(encoding="utf-8"))
    expected = {f"FR-{number:03}" for number in range(1, 26)}

    assert set(traceability) == expected
    for requirement in traceability.values():
        assert requirement["implementation"]
        assert requirement["tests"]
        assert requirement["cases"]
