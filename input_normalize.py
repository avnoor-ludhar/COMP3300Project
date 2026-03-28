from __future__ import annotations

from typing import Any


def normalize_dict_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            (k.strip() if isinstance(k, str) else k): normalize_dict_keys(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [normalize_dict_keys(x) for x in obj]
    return obj


def _normalize_job_strings(job: Any) -> Any:
    if not isinstance(job, dict):
        return job
    out = dict(job)
    if "pid" in out and out["pid"] is not None:
        out["pid"] = str(out["pid"]).strip()
    return out


def normalize_input(data: dict) -> dict:
    normalized = normalize_dict_keys(data)
    if not isinstance(normalized, dict):
        return normalized
    if isinstance(normalized.get("jobs"), list):
        normalized["jobs"] = [
            _normalize_job_strings(j) for j in normalized["jobs"]
        ]
    if "policy" in normalized and normalized["policy"] is not None:
        normalized["policy"] = str(normalized["policy"]).strip()
    return normalized
