import json
import sys

from metrics import compute_metrics
from scheduler import Scheduler, gantt_to_dicts
from task import Task


def format_schedule_json(data: dict) -> str:
    return json.dumps(data, indent=2, allow_nan=False) + "\n"


def parse_tasks(json_load) -> Scheduler:
    # Parse JSON input into Scheduler object. Quantum defaults to 0 for non-RR policies.
    jobs = json_load["jobs"]
    parsed_jobs = [
        Task(j["pid"], j["arrival"], j["burst"], j["priority"]) for j in jobs
    ]
    quantum = json_load.get("quantum", 0)  # only required for RR
    policy = str(json_load["policy"]).strip().upper()
    return Scheduler(policy, parsed_jobs, quantum)


def build_output(scheduler: Scheduler, gantt) -> dict:
    # Construct final output dict with policy, Gantt chart, and computed metrics.
    policy = scheduler.policy.strip().upper()
    return {
        "policy": policy,
        "gantt": gantt_to_dicts(gantt),
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
