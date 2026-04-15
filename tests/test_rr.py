import json
from pathlib import Path

from main import build_output, parse_tasks

_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "rr"


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


# Test 1: Basic RR from original fixture
def test_rr_basic():
    _load_and_test("basic", {
        "policy": "RR",
        "gantt": [
            {"pid": "A", "start": 0, "end": 2},
            {"pid": "B", "start": 2, "end": 4},
            {"pid": "C", "start": 4, "end": 6},
            {"pid": "A", "start": 6, "end": 8},
            {"pid": "B", "start": 8, "end": 10},
            {"pid": "C", "start": 10, "end": 11},
            {"pid": "A", "start": 11, "end": 13},
        ],
        "metrics": {
            "turnaround": {"A": 13, "B": 10, "C": 11},
            "waiting": {"A": 7, "B": 6, "C": 8},
            "avg_turnaround": 11.33,
            "avg_waiting": 7.0,
        },
    })


# Test 2: Single task
def test_rr_single_task():
    _load_and_test("single_task", {
        "policy": "RR",
        "gantt": [
            {"pid": "A", "start": 0, "end": 2},
            {"pid": "A", "start": 2, "end": 4},
            {"pid": "A", "start": 4, "end": 5},
        ],
        "metrics": {
            "turnaround": {"A": 5},
            "waiting": {"A": 0},
            "avg_turnaround": 5.0,
            "avg_waiting": 0.0,
        },
    })


# Test 3: Quantum larger than burst times
def test_rr_large_quantum():
    _load_and_test("large_quantum", {
        "policy": "RR",
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


# Test 4: Quantum = 1
def test_rr_quantum_one():
    _load_and_test("quantum_one", {
        "policy": "RR",
        "gantt": [
            {"pid": "A", "start": 0, "end": 1},
            {"pid": "B", "start": 1, "end": 2},
            {"pid": "A", "start": 2, "end": 3},
            {"pid": "B", "start": 3, "end": 4},
            {"pid": "A", "start": 4, "end": 5},
        ],
        "metrics": {
            "turnaround": {"A": 5, "B": 4},
            "waiting": {"A": 2, "B": 2},
            "avg_turnaround": 4.5,
            "avg_waiting": 2.0,
        },
    })


# Test 5: All tasks arrive at same time
def test_rr_all_arrive_together():
    _load_and_test("all_arrive_together", {
        "policy": "RR",
        "gantt": [
            {"pid": "A", "start": 0, "end": 2},
            {"pid": "B", "start": 2, "end": 4},
            {"pid": "C", "start": 4, "end": 6},
            {"pid": "A", "start": 6, "end": 8},
            {"pid": "B", "start": 8, "end": 9},
        ],
        "metrics": {
            "turnaround": {"A": 8, "B": 9, "C": 6},
            "waiting": {"A": 4, "B": 6, "C": 4},
            "avg_turnaround": 7.67,
            "avg_waiting": 4.67,
        },
    })


# Test 6: Task arrives exactly at quantum boundary
def test_rr_arrival_at_boundary():
    _load_and_test("arrival_at_boundary", {
        "policy": "RR",
        "gantt": [
            {"pid": "A", "start": 0, "end": 2},
            {"pid": "A", "start": 2, "end": 4},
            {"pid": "B", "start": 4, "end": 6},
            {"pid": "A", "start": 6, "end": 8},
            {"pid": "B", "start": 8, "end": 10},
        ],
        "metrics": {
            "turnaround": {"A": 8, "B": 8},
            "waiting": {"A": 2, "B": 4},
            "avg_turnaround": 8.0,
            "avg_waiting": 3.0,
        },
    })


# Test 7: Late arriving task
def test_rr_late_arrival():
    _load_and_test("late_arrival", {
        "policy": "RR",
        "gantt": [
            {"pid": "A", "start": 0, "end": 2},
            {"pid": "A", "start": 2, "end": 4},
            {"pid": "B", "start": 5, "end": 7},
            {"pid": "B", "start": 7, "end": 8},
        ],
        "metrics": {
            "turnaround": {"A": 4, "B": 3},
            "waiting": {"A": 0, "B": 0},
            "avg_turnaround": 3.5,
            "avg_waiting": 0.0,
        },
    })


# Test 8: Three tasks with different arrival and burst
def test_rr_three_tasks_complex():
    _load_and_test("three_tasks_complex", {
        "policy": "RR",
        "gantt": [
            {"pid": "A", "start": 0, "end": 3},
            {"pid": "B", "start": 3, "end": 6},
            {"pid": "A", "start": 6, "end": 9},
            {"pid": "C", "start": 9, "end": 11},
            {"pid": "B", "start": 11, "end": 12},
            {"pid": "A", "start": 12, "end": 14},
        ],
        "metrics": {
            "turnaround": {"A": 14, "B": 11, "C": 8},
            "waiting": {"A": 6, "B": 7, "C": 6},
            "avg_turnaround": 11.0,
            "avg_waiting": 6.33,
        },
    })


# Test 9: Empty job list returns empty output
def test_rr_empty_jobs():
    _load_and_test("empty_jobs", {
        "policy": "RR",
        "gantt": [],
        "metrics": {
            "turnaround": {},
            "waiting": {},
            "avg_turnaround": 0.0,
            "avg_waiting": 0.0,
        },
    })
