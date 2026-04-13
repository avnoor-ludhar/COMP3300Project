import json
from pathlib import Path

from main import build_output, parse_tasks

_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "fifo"


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


# Test 1: Basic FIFO from original fixture
def test_fifo_basic():
    _load_and_test("basic", {
        "policy": "FIFO",
        "gantt": [
            {"pid": "A", "start": 0, "end": 4},
            {"pid": "B", "start": 4, "end": 6},
        ],
        "metrics": {
            "turnaround": {"A": 4, "B": 5},
            "waiting": {"A": 0, "B": 3},
            "avg_turnaround": 4.5,
            "avg_waiting": 1.5,
        },
    })


# Test 2: Single task
def test_fifo_single_task():
    _load_and_test("single_task", {
        "policy": "FIFO",
        "gantt": [{"pid": "A", "start": 0, "end": 5}],
        "metrics": {
            "turnaround": {"A": 5},
            "waiting": {"A": 0},
            "avg_turnaround": 5.0,
            "avg_waiting": 0.0,
        },
    })


# Test 3: All arrive at same time (tie-break by PID)
def test_fifo_all_arrive_same_time():
    _load_and_test("all_same_time", {
        "policy": "FIFO",
        "gantt": [
            {"pid": "A", "start": 0, "end": 3},
            {"pid": "B", "start": 3, "end": 5},
            {"pid": "C", "start": 5, "end": 9},
        ],
        "metrics": {
            "turnaround": {"A": 3, "B": 5, "C": 9},
            "waiting": {"A": 0, "B": 3, "C": 5},
            "avg_turnaround": 5.67,
            "avg_waiting": 2.67,
        },
    })


# Test 4: Idle time between tasks
def test_fifo_with_idle_time():
    _load_and_test("idle_time", {
        "policy": "FIFO",
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


# Test 5: Reverse arrival order
def test_fifo_reverse_arrival():
    _load_and_test("reverse_arrival", {
        "policy": "FIFO",
        "gantt": [
            {"pid": "C", "start": 0, "end": 4},
            {"pid": "B", "start": 4, "end": 6},
            {"pid": "A", "start": 6, "end": 9},
        ],
        "metrics": {
            "turnaround": {"A": 4, "B": 4, "C": 4},
            "waiting": {"A": 1, "B": 2, "C": 0},
            "avg_turnaround": 4.0,
            "avg_waiting": 1.0,
        },
    })


# Test 6: Boundary arrival (task arrives exactly when other finishes)
def test_fifo_boundary_arrival():
    _load_and_test("boundary_arrival", {
        "policy": "FIFO",
        "gantt": [
            {"pid": "A", "start": 0, "end": 3},
            {"pid": "B", "start": 3, "end": 5},
        ],
        "metrics": {
            "turnaround": {"A": 3, "B": 2},
            "waiting": {"A": 0, "B": 0},
            "avg_turnaround": 2.5,
            "avg_waiting": 0.0,
        },
    })


# Test 7: Four tasks with mixed arrivals
def test_fifo_four_tasks():
    _load_and_test("four_tasks", {
        "policy": "FIFO",
        "gantt": [
            {"pid": "A", "start": 0, "end": 2},
            {"pid": "B", "start": 2, "end": 5},
            {"pid": "C", "start": 5, "end": 6},
            {"pid": "D", "start": 6, "end": 8},
        ],
        "metrics": {
            "turnaround": {"A": 2, "B": 5, "C": 5, "D": 6},
            "waiting": {"A": 0, "B": 2, "C": 4, "D": 4},
            "avg_turnaround": 4.5,
            "avg_waiting": 2.5,
        },
    })


# Test 8: Late arriving task (after first completes)
def test_fifo_late_arrival():
    _load_and_test("late_arrival", {
        "policy": "FIFO",
        "gantt": [
            {"pid": "A", "start": 0, "end": 4},
            {"pid": "B", "start": 10, "end": 12},
        ],
        "metrics": {
            "turnaround": {"A": 4, "B": 2},
            "waiting": {"A": 0, "B": 0},
            "avg_turnaround": 3.0,
            "avg_waiting": 0.0,
        },
    })
