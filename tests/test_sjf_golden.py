import json
from pathlib import Path

import pytest

from input_normalize import normalize_input
from input_validate import validate_input
from main import build_output, parse_tasks

_FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"

_EXPECTED_SJF = {
    "policy": "SJF",
    "gantt": [
        {"pid": "B", "start": 0, "end": 2},
        {"pid": "D", "start": 2, "end": 3},
        {"pid": "C", "start": 3, "end": 5},
        {"pid": "A", "start": 5, "end": 10},
    ],
    "metrics": {
        "turnaround": {"A": 10, "B": 2, "C": 4, "D": 1},
        "waiting": {"A": 5, "B": 0, "C": 2, "D": 0},
        "avg_turnaround": 4.25,
        "avg_waiting": 1.75,
    },
}


def test_sjf_golden_matches_fixture_file():
    path = _FIXTURE_DIR / "sjf.json"
    assert path.is_file(), f"missing fixture: {path}"
    raw = json.loads(path.read_text(encoding="utf-8"))
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert out == _EXPECTED_SJF


def test_sjf_equal_burst_uses_lexicographic_pid_tiebreak():
    raw = {
        "policy": "SJF",
        "jobs": [
            {"pid": "B", "arrival": 0, "burst": 2, "priority": 1},
            {"pid": "A", "arrival": 0, "burst": 2, "priority": 1},
            {"pid": "C", "arrival": 0, "burst": 3, "priority": 1},
        ],
    }
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert [x["pid"] for x in out["gantt"]] == ["A", "B", "C"]


@pytest.mark.parametrize("policy_spacing", ["SJF", "  sjf  "])
def test_sjf_policy_normalization(policy_spacing: str):
    raw = {
        "policy": policy_spacing,
        "jobs": [
            {"pid": "A", "arrival": 0, "burst": 5, "priority": 3},
            {"pid": "B", "arrival": 0, "burst": 2, "priority": 1},
            {"pid": "C", "arrival": 1, "burst": 2, "priority": 2},
            {"pid": "D", "arrival": 2, "burst": 1, "priority": 2},
        ],
    }
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert out == _EXPECTED_SJF
