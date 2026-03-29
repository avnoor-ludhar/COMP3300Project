import json
from pathlib import Path

from main import build_output, parse_tasks


def test_pytest_setup_and_imports_work():
    """Phase 4.1 smoke test: pytest discovery and local imports work."""
    data = {
        "policy": "FIFO",
        "jobs": [{"pid": "X", "arrival": 0, "burst": 2, "priority": 1}],
    }
    scheduler = parse_tasks(data)
    gantt = scheduler.schedule()
    out = build_output(scheduler, gantt)

    assert out["policy"] == "FIFO"
    assert out["gantt"] == [{"pid": "X", "start": 0, "end": 2}]
    assert out["metrics"]["turnaround"] == {"X": 2}
    assert out["metrics"]["waiting"] == {"X": 0}
    json.dumps(out)


def test_project_root_contains_expected_entrypoint():
    assert (Path(__file__).resolve().parents[1] / "main.py").exists()
