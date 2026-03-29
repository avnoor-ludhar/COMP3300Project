import json
from pathlib import Path

import pytest

from input_normalize import normalize_input
from input_validate import validate_input
from main import build_output, parse_tasks

_FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"

_EXPECTED_FIFO = {
    "policy": "FIFO",
    "gantt": [
        {"pid": "A", "start": 0, "end": 4},
        {"pid": "B", "start": 4, "end": 6},
    ],
    "metrics": {
        "turnaround": {"A": 4, "B": 4},
        "waiting": {"A": 0, "B": 2},
        "avg_turnaround": 4.0,
        "avg_waiting": 1.0,
    },
}


def test_fifo_golden_matches_fixture_file():
    path = _FIXTURE_DIR / "fifo.json"
    assert path.is_file(), f"missing fixture: {path}"
    raw = json.loads(path.read_text(encoding="utf-8"))
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert out == _EXPECTED_FIFO


def test_fifo_equal_arrival_uses_lexicographic_pid_tiebreak():
    raw = {
        "policy": "FIFO",
        "jobs": [
            {"pid": "B", "arrival": 0, "burst": 3, "priority": 1},
            {"pid": "A", "arrival": 0, "burst": 2, "priority": 1},
        ],
    }
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert [x["pid"] for x in out["gantt"]] == ["A", "B"]
    assert out["gantt"] == [
        {"pid": "A", "start": 0, "end": 2},
        {"pid": "B", "start": 2, "end": 5},
    ]
    assert out["metrics"]["turnaround"] == {"A": 2, "B": 5}
    assert out["metrics"]["waiting"] == {"A": 0, "B": 2}
    assert out["metrics"]["avg_turnaround"] == 3.5
    assert out["metrics"]["avg_waiting"] == 1.0


@pytest.mark.parametrize("policy_spacing", ["FIFO", "  fifo  "])
def test_fifo_policy_normalization(policy_spacing: str):
    raw = {
        "policy": policy_spacing,
        "jobs": [
            {"pid": "A", "arrival": 0, "burst": 4, "priority": 1},
            {"pid": "B", "arrival": 2, "burst": 2, "priority": 1},
        ],
    }
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert out == _EXPECTED_FIFO
