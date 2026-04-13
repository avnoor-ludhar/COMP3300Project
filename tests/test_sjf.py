import json
from pathlib import Path

from main import build_output, parse_tasks

_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "sjf"


def _load_and_test(fixture_name: str, expected: dict):
    """Helper to load a fixture and assert against expected output.
    Mirrors the logic in main.py for file loading and JSON parsing.
    """
    fixture_path = _FIXTURES / f"{fixture_name}.json"
    with open(fixture_path) as f:
        json_load = json.load(f)
    scheduler = parse_tasks(json_load)
    gantt = scheduler.schedule()
    out = build_output(scheduler, gantt)
    assert out == expected


# Test 1: Basic SJF from original fixture
def test_sjf_basic():
    _load_and_test("basic", {
        "policy": "SJF",
        "gantt": [
            {"pid": "D", "start": 0, "end": 1},
            {"pid": "B", "start": 1, "end": 3},
            {"pid": "A", "start": 3, "end": 9},
            {"pid": "C", "start": 9, "end": 17},
        ],
        "metrics": {
            "turnaround": {"A": 9, "B": 3, "C": 17, "D": 1},
            "waiting": {"A": 3, "B": 1, "C": 9, "D": 0},
            "avg_turnaround": 7.5,
            "avg_waiting": 3.25,
        },
    })


# Test 2: Single task
def test_sjf_single_task():
    _load_and_test("single_task", {
        "policy": "SJF",
        "gantt": [{"pid": "A", "start": 0, "end": 5}],
        "metrics": {
            "turnaround": {"A": 5},
            "waiting": {"A": 0},
            "avg_turnaround": 5.0,
            "avg_waiting": 0.0,
        },
    })


# Test 3: Same burst tie-break by PID
def test_sjf_same_burst_tie_break():
    _load_and_test("same_burst_tie_break", {
        "policy": "SJF",
        "gantt": [
            {"pid": "C", "start": 0, "end": 2},
            {"pid": "A", "start": 2, "end": 5},
            {"pid": "B", "start": 5, "end": 8},
        ],
        "metrics": {
            "turnaround": {"A": 5, "B": 8, "C": 2},
            "waiting": {"A": 2, "B": 5, "C": 0},
            "avg_turnaround": 5.0,
            "avg_waiting": 2.33,
        },
    })


# Test 4: Short job arrives after long job starts (non-preemptive)
def test_sjf_short_job_arrives_later():
    _load_and_test("short_job_arrives_later", {
        "policy": "SJF",
        "gantt": [
            {"pid": "A", "start": 0, "end": 6},
            {"pid": "B", "start": 6, "end": 8},
        ],
        "metrics": {
            "turnaround": {"A": 6, "B": 6},
            "waiting": {"A": 0, "B": 4},
            "avg_turnaround": 6.0,
            "avg_waiting": 2.0,
        },
    })


# Test 5: All arrive together, varying burst times
def test_sjf_all_arrive_together():
    _load_and_test("all_arrive_together", {
        "policy": "SJF",
        "gantt": [
            {"pid": "D", "start": 0, "end": 1},
            {"pid": "B", "start": 1, "end": 3},
            {"pid": "C", "start": 3, "end": 6},
            {"pid": "A", "start": 6, "end": 11},
        ],
        "metrics": {
            "turnaround": {"A": 11, "B": 3, "C": 6, "D": 1},
            "waiting": {"A": 6, "B": 1, "C": 3, "D": 0},
            "avg_turnaround": 5.25,
            "avg_waiting": 2.5,
        },
    })


# Test 6: Long job first, shorter jobs arrive later (must wait)
def test_sjf_long_first_short_later():
    _load_and_test("long_first_short_later", {
        "policy": "SJF",
        "gantt": [
            {"pid": "B", "start": 0, "end": 4},
            {"pid": "C", "start": 4, "end": 5},
            {"pid": "A", "start": 5, "end": 13},
        ],
        "metrics": {
            "turnaround": {"A": 13, "B": 4, "C": 4},
            "waiting": {"A": 5, "B": 0, "C": 3},
            "avg_turnaround": 7.0,
            "avg_waiting": 2.67,
        },
    })


# Test 7: Idle time between tasks
def test_sjf_with_idle_time():
    _load_and_test("idle_time", {
        "policy": "SJF",
        "gantt": [
            {"pid": "A", "start": 0, "end": 2},
            {"pid": "B", "start": 5, "end": 8},
        ],
        "metrics": {
            "turnaround": {"A": 2, "B": 3},
            "waiting": {"A": 0, "B": 0},
            "avg_turnaround": 2.5,
            "avg_waiting": 0.0,
        },
    })


# Test 8: Staggered arrivals with varying burst times
def test_sjf_staggered_arrivals():
    _load_and_test("staggered_arrivals", {
        "policy": "SJF",
        "gantt": [
            {"pid": "A", "start": 0, "end": 6},
            {"pid": "C", "start": 6, "end": 7},
            {"pid": "D", "start": 7, "end": 9},
            {"pid": "B", "start": 9, "end": 12},
        ],
        "metrics": {
            "turnaround": {"A": 6, "B": 11, "C": 5, "D": 6},
            "waiting": {"A": 0, "B": 8, "C": 4, "D": 4},
            "avg_turnaround": 7.0,
            "avg_waiting": 4.0,
        },
    })
