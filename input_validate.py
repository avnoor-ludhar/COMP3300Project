from __future__ import annotations

ALLOWED_POLICIES = frozenset({"FIFO", "SJF", "RR", "PRIORITY"})


def _as_int(label: str, value: object) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be an integer (got boolean)")
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    raise ValueError(f"{label} must be an integer")


def validate_input(data: object) -> None:
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")

    if "policy" not in data:
        raise ValueError("Missing required field: policy")
    pol = data["policy"]
    if pol is None or (isinstance(pol, str) and not pol.strip()):
        raise ValueError("policy must be a non-empty string")
    policy_upper = str(pol).strip().upper()
    if policy_upper not in ALLOWED_POLICIES:
        raise ValueError(f"Unsupported policy: {pol!r}")

    if "jobs" not in data:
        raise ValueError("Missing required field: jobs")
    jobs = data["jobs"]
    if not isinstance(jobs, list):
        raise ValueError("jobs must be a list")
    if len(jobs) == 0:
        raise ValueError("jobs must not be empty")

    seen_pids: set[str] = set()
    for i, job in enumerate(jobs):
        if not isinstance(job, dict):
            raise ValueError(f"jobs[{i}] must be an object")
        for field in ("pid", "arrival", "burst", "priority"):
            if field not in job:
                raise ValueError(f"jobs[{i}] missing required field: {field}")

        pid = job["pid"]
        if not isinstance(pid, str) or not pid:
            raise ValueError(f"jobs[{i}].pid must be a non-empty string")
        if pid in seen_pids:
            raise ValueError(f"Duplicate pid: {pid!r}")
        seen_pids.add(pid)

        arrival = _as_int(f"jobs[{i}].arrival", job["arrival"])
        burst = _as_int(f"jobs[{i}].burst", job["burst"])
        priority = _as_int(f"jobs[{i}].priority", job["priority"])
        if arrival < 0:
            raise ValueError(f"jobs[{i}].arrival must be >= 0")
        if burst < 1:
            raise ValueError(f"jobs[{i}].burst must be >= 1")

        job["arrival"] = arrival
        job["burst"] = burst
        job["priority"] = priority

    if policy_upper == "RR":
        if "quantum" not in data or data["quantum"] is None:
            raise ValueError("RR policy requires a quantum field")
        q = _as_int("quantum", data["quantum"])
        if q < 1:
            raise ValueError("quantum must be >= 1 for RR")
        data["quantum"] = q
    elif "quantum" in data and data["quantum"] is not None:
        q = _as_int("quantum", data["quantum"])
        if q < 0:
            raise ValueError("quantum must be >= 0")
        data["quantum"] = q
