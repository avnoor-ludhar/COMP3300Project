import json
import sys
from typing import List

from metrics import compute_metrics
from scheduler import GanttObject, Scheduler
from task import Task


def format_schedule_json(data: dict) -> str:
    # Custom JSON formatter for compact array output with readable structure.
    policy = json.dumps(data["policy"], allow_nan=False)
    gantt = data["gantt"]
    m = data["metrics"]

    lines = ["{"]
    lines.append(f'  "policy": {policy},')
    lines.append('  "gantt": [')
    for i, seg in enumerate(gantt):
        seg_json = json.dumps(seg, allow_nan=False, separators=(", ", ": "))
        tail = "," if i < len(gantt) - 1 else ""
        lines.append(f"    {seg_json}{tail}")
    lines.append("  ],")
    lines.append('  "metrics": {')
    lines.append(f'    "turnaround": {json.dumps(m["turnaround"], allow_nan=False, separators=(", ", ": "))},')
    lines.append(f'    "waiting": {json.dumps(m["waiting"], allow_nan=False, separators=(", ", ": "))},')
    lines.append(f'    "avg_turnaround": {json.dumps(m["avg_turnaround"], allow_nan=False)},')
    lines.append(f'    "avg_waiting": {json.dumps(m["avg_waiting"], allow_nan=False)}')
    lines.append("  }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def parse_tasks(json_load) -> Scheduler:
    # Parse JSON input into Scheduler object. Quantum defaults to 0 for non-RR policies.
    jobs = json_load["jobs"]
    parsed_jobs = [
        Task(j["pid"], j["arrival"], j["burst"], j["priority"]) for j in jobs
    ]
    quantum = json_load.get("quantum", 0)  # only required for RR
    policy = str(json_load["policy"]).strip().upper()
    return Scheduler(policy, parsed_jobs, quantum)


def build_output(scheduler: Scheduler, gantt: List[GanttObject]) -> dict:
    # Construct final output dict with policy, Gantt chart, and computed metrics.
    policy = scheduler.policy.strip().upper()
    gantt_dicts = [seg.to_dict() for seg in gantt]  # convert GanttObjects to dicts
    return {
        "policy": policy,
        "gantt": gantt_dicts,
        "metrics": compute_metrics(scheduler.jobs),
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <input.json>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file) as f:
        json_load = json.load(f)

    scheduler = parse_tasks(json_load)
    gantt = scheduler.schedule()
    out = build_output(scheduler, gantt)

    print(format_schedule_json(out))
