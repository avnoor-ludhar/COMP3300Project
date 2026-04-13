from __future__ import annotations

from typing import List

from task import Task


def compute_metrics(tasks: List[Task]) -> dict:
    # Calculate turnaround and waiting times for each task plus averages.
    if not tasks:
        raise ValueError("Cannot compute metrics for an empty job list")
    for task in tasks:
        if task.finish_time is None:
            raise ValueError(
                f"Task {task.pid!r} has no finish_time. Run the scheduler first"
            )

    ordered = sorted(tasks, key=lambda t: t.pid)  # deterministic ordering by PID
    turnaround: dict[str, int] = {}
    waiting: dict[str, int] = {}
    for task in ordered:
        turnaround[task.pid] = task.turnaround_time()
        waiting[task.pid] = task.waiting_time()

    n = len(ordered)
    return {
        "turnaround": turnaround,
        "waiting": waiting,
        "avg_turnaround": round(sum(turnaround.values()) / n, 2),
        "avg_waiting": round(sum(waiting.values()) / n, 2),
    }
