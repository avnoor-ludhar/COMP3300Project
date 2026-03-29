import json
import subprocess
import sys
from pathlib import Path

import pytest

from input_normalize import normalize_input
from input_validate import validate_input
from main import build_output, parse_tasks

_ROOT = Path(__file__).resolve().parents[1]
_MAIN = _ROOT / "main.py"


def _run_main_with_temp_json(tmp_path: Path, payload: dict) -> subprocess.CompletedProcess[str]:
    path = tmp_path / "input.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(_MAIN), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("payload", "expected_substring"),
    [
        (
            {"policy": "RR", "jobs": [{"pid": "A", "arrival": 0, "burst": 1, "priority": 1}]},
            "RR policy requires a quantum field",
        ),
        ({"policy": "FIFO", "jobs": []}, "jobs must not be empty"),
        (
            {
                "policy": "FIFO",
                "jobs": [
                    {"pid": "A", "arrival": 0, "burst": 1, "priority": 1},
                    {"pid": "A", "arrival": 1, "burst": 1, "priority": 1},
                ],
            },
            "Duplicate pid",
        ),
    ],
)
def test_invalid_inputs_exit_nonzero_and_emit_stderr(
    tmp_path: Path, payload: dict, expected_substring: str
):
    cp = _run_main_with_temp_json(tmp_path, payload)
    assert cp.returncode == 1
    assert expected_substring in cp.stderr
    assert cp.stdout == ""


def test_idle_cpu_edge_case_fast_forwards_to_first_arrival():
    raw = {
        "policy": "FIFO",
        "jobs": [{"pid": "LATE", "arrival": 5, "burst": 3, "priority": 1}],
    }
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert out["gantt"] == [{"pid": "LATE", "start": 5, "end": 8}]
    assert out["metrics"]["turnaround"] == {"LATE": 3}
    assert out["metrics"]["waiting"] == {"LATE": 0}


def test_single_job_edge_case_has_zero_waiting():
    raw = {
        "policy": "SJF",
        "jobs": [{"pid": "ONLY", "arrival": 0, "burst": 4, "priority": 2}],
    }
    data = normalize_input(raw)
    validate_input(data)
    scheduler = parse_tasks(data)
    out = build_output(scheduler, scheduler.schedule())
    assert out["gantt"] == [{"pid": "ONLY", "start": 0, "end": 4}]
    assert out["metrics"]["turnaround"] == {"ONLY": 4}
    assert out["metrics"]["waiting"] == {"ONLY": 0}
    assert out["metrics"]["avg_turnaround"] == 4.0
    assert out["metrics"]["avg_waiting"] == 0.0


def test_messy_key_normalization_matches_clean_input():
    clean = {
        "policy": "RR",
        "quantum": 2,
        "jobs": [
            {"pid": "A", "arrival": 0, "burst": 6, "priority": 3},
            {"pid": "B", "arrival": 4, "burst": 4, "priority": 1},
            {"pid": "C", "arrival": 6, "burst": 3, "priority": 2},
        ],
    }
    messy = {
        " policy ": "  rr  ",
        " quantum ": 2,
        " jobs ": [
            {" pid ": " A ", " arrival ": 0, " burst ": 6, " priority ": 3},
            {" pid ": " B ", " arrival ": 4, " burst ": 4, " priority ": 1},
            {" pid ": " C ", " arrival ": 6, " burst ": 3, " priority ": 2},
        ],
    }
    clean_data = normalize_input(clean)
    validate_input(clean_data)
    clean_scheduler = parse_tasks(clean_data)
    clean_out = build_output(clean_scheduler, clean_scheduler.schedule())

    messy_data = normalize_input(messy)
    validate_input(messy_data)
    messy_scheduler = parse_tasks(messy_data)
    messy_out = build_output(messy_scheduler, messy_scheduler.schedule())

    assert messy_out == clean_out
