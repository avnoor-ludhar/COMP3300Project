import json
from pathlib import Path

from main import build_output, parse_tasks

_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "priority"


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


# Test 1: Basic Priority from original fixture
def test_priority_basic():
    _load_and_test("basic", {
        "policy": "PRIORITY",
        "gantt": [
            {"pid": "B", "start": 0, "end": 2},
            {"pid": "C", "start": 2, "end": 5},
            {"pid": "A", "start": 5, "end": 9},
            {"pid": "D", "start": 9, "end": 10},
        ],
        "metrics": {
            "turnaround": {"A": 9, "B": 2, "C": 5, "D": 10},
            "waiting": {"A": 5, "B": 0, "C": 2, "D": 9},
            "avg_turnaround": 6.5,
            "avg_waiting": 4.0,
        },
    })


# Test 2: Single task
def test_priority_single_task():
    _load_and_test("single_task", {
        "policy": "PRIORITY",
        "gantt": [{"pid": "A", "start": 0, "end": 5}],
        "metrics": {
            "turnaround": {"A": 5},
            "waiting": {"A": 0},
            "avg_turnaround": 5.0,
            "avg_waiting": 0.0,
        },
    })


# Test 3: All same priority (tie-break by PID via heap ordering)
def test_priority_same_priority():
    _load_and_test("same_priority", {
        "policy": "PRIORITY",
        "gantt": [
            {"pid": "A", "start": 0, "end": 4},
            {"pid": "B", "start": 4, "end": 6},
            {"pid": "C", "start": 6, "end": 9},
        ],
        "metrics": {
            "turnaround": {"A": 4, "B": 6, "C": 9},
            "waiting": {"A": 0, "B": 4, "C": 6},
            "avg_turnaround": 6.33,
            "avg_waiting": 3.33,
        },
    })


# Test 4: Higher priority arrives later - CPU continues current
def test_priority_high_priority_arrives_later():
    _load_and_test("high_priority_arrives_later", {
        "policy": "PRIORITY",
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


# Test 5: All arrive at once, different priorities
def test_priority_all_arrive_together():
    _load_and_test("all_arrive_together", {
        "policy": "PRIORITY",
        "gantt": [
            {"pid": "B", "start": 0, "end": 2},
            {"pid": "C", "start": 2, "end": 5},
            {"pid": "A", "start": 5, "end": 9},
            {"pid": "D", "start": 9, "end": 10},
        ],
        "metrics": {
            "turnaround": {"A": 9, "B": 2, "C": 5, "D": 10},
            "waiting": {"A": 5, "B": 0, "C": 2, "D": 9},
            "avg_turnaround": 6.5,
            "avg_waiting": 4.0,
        },
    })


# Test 6: Priority with staggered arrivals
def test_priority_staggered_arrivals():
    _load_and_test("staggered_arrivals", {
        "policy": "PRIORITY",
        "gantt": [
            {"pid": "A", "start": 0, "end": 5},
            {"pid": "B", "start": 5, "end": 7},
            {"pid": "D", "start": 7, "end": 8},
            {"pid": "C", "start": 8, "end": 11},
        ],
        "metrics": {
            "turnaround": {"A": 5, "B": 6, "C": 9, "D": 5},
            "waiting": {"A": 0, "B": 4, "C": 6, "D": 4},
            "avg_turnaround": 6.25,
            "avg_waiting": 3.5,
        },
    })


# Test 7: Lower priority number = higher priority
def test_priority_lower_is_higher():
    _load_and_test("lower_is_higher", {
        "policy": "PRIORITY",
        "gantt": [
            {"pid": "B", "start": 0, "end": 2},
            {"pid": "A", "start": 2, "end": 5},
        ],
        "metrics": {
            "turnaround": {"A": 5, "B": 2},
            "waiting": {"A": 2, "B": 0},
            "avg_turnaround": 3.5,
            "avg_waiting": 1.0,
        },
    })


# Test 8: Idle time with priority
def test_priority_with_idle_time():
    _load_and_test("idle_time", {
        "policy": "PRIORITY",
        "gantt": [
            {"pid": "A", "start": 0, "end": 2},
            {"pid": "B", "start": 5, "end": 8},
            {"pid": "C", "start": 8, "end": 10},
        ],
        "metrics": {
            "turnaround": {"A": 2, "B": 3, "C": 5},
            "waiting": {"A": 0, "B": 0, "C": 3},
            "avg_turnaround": 3.33,
            "avg_waiting": 1.0,
        },
    })
