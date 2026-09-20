"""Week 8 release runner: execute an integrated upstream assistant live."""
from __future__ import annotations

import argparse
import json
import math
import os
import pathlib
import statistics
import time

from integration.runtime import LiveRuntimeError, execute_live

ROOT = pathlib.Path(__file__).resolve().parent
DATA, REPORTS = ROOT / "data", ROOT / "reports"
REQUIRED_FAILURES = {"model_unavailable", "retrieval_down", "tool_timeout", "database_timeout", "approval_timeout"}


def load_rows():
    path = DATA / "release.jsonl"
    if not path.exists(): path = DATA / "sample.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def p95(values):
    values = sorted(values)
    return values[max(0, min(len(values) - 1, math.ceil(.95 * len(values)) - 1))] if values else 0.0


def smoke_case(row, index):
    """Only `make run` may use this explicit, non-promotable fixture."""
    started = time.perf_counter(); failure = row.get("failure", "none")
    observed = {"model_unavailable": "recovered", "retrieval_down": "bounded_failure", "tool_timeout": "recovered", "database_timeout": "degraded", "approval_timeout": "approval_pending"}.get(failure, "completed")
    return {"case_id": row["case_id"], "request_id": f"smoke-{index+1}", "failure": failure, "risk": row.get("risk", "low"), "observed": observed, "bounded": True, "policy": "smoke_only", "success": True, "latency_ms": round((time.perf_counter()-started)*1000, 3), "cost_usd": 0.0, "trace_id": f"smoke-{index+1:04d}", "execution_mode": "smoke_fixture", "components": {"notice": "No upstream runtime was called. This row cannot be promoted."}}


def _failure_matrix(raw):
    matrix = {}
    for failure in REQUIRED_FAILURES:
        rows = [r for r in raw if r["failure"] == failure]
        matrix[failure] = {"cases": len(rows), "recovery_success_rate": sum(r["success"] for r in rows) / len(rows) if rows else 0.0, "p95_latency_ms": p95([r["latency_ms"] for r in rows]), "outcomes": sorted({r["observed"] for r in rows})}
    return matrix


def run(rows, course_work_root=None, smoke=False):
    if smoke: raw = [smoke_case(row, i) for i, row in enumerate(rows)]
    else:
        if not course_work_root: raise LiveRuntimeError("live release needs --course-work-root")
        raw = [execute_live(course_work_root, row, i) for i, row in enumerate(rows)]
    latencies, costs = [r["latency_ms"] for r in raw], [r["cost_usd"] for r in raw]; successes = sum(r["success"] for r in raw)
    latency_slo, cost_slo = float(os.getenv("LATENCY_SLO_MS", "250")), float(os.getenv("COST_SLO_USD", "0.01"))
    metrics = {"schema_version": 2, "week": 8, "release_version": os.getenv("RELEASE_VERSION", "week8-local"), "cases": len(raw), "success_rate": successes / len(raw) if raw else 0.0, "latency_p50_ms": statistics.median(latencies) if latencies else 0.0, "latency_p95_ms": p95(latencies), "cost_total_usd": sum(costs), "cost_per_successful_task": sum(costs) / (successes or 1), "error_rate": sum(not r["success"] for r in raw) / len(raw) if raw else 0.0, "slo": {"latency_budget_ms": latency_slo, "cost_budget_usd": cost_slo, "latency_pass": p95(latencies) <= latency_slo, "cost_pass": sum(costs)/(successes or 1) <= cost_slo}, "failure_matrix": _failure_matrix(raw), "observability": {"trace_count": len({r["trace_id"] for r in raw}), "log_count": sum(len(r.get("components", {}).get("workflow", {}).get("journal", [])) for r in raw)}, "security": {"high_risk_cases": sum(r["risk"] == "high" for r in raw), "high_risk_without_policy": sum(r["risk"] == "high" and r["policy"] != "deny" for r in raw)}, "execution": {"mode": "smoke_fixture" if smoke else "live_coursework", "components": ["week2_retrieval", "week3_mcp", "week4_planner_executor", "week5_security", "week6_adapter", "week7_workflow"], "course_work_root": str(course_work_root) if course_work_root else None}, "raw_results": raw}
    return raw, metrics


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--allow-sample", action="store_true"); ap.add_argument("--require-real-data", action="store_true"); ap.add_argument("--course-work-root", type=pathlib.Path, default=os.getenv("COURSE_WORK_ROOT")); args = ap.parse_args()
    manifest = json.loads((DATA / "manifest.json").read_text()); upstream = DATA / "upstream-evidence.json"; smoke = bool(args.allow_sample)
    if args.require_real_data:
        if manifest.get("status") != "materialized" or not upstream.exists(): raise SystemExit("materialized release required: python scripts/fetch_data.py --cases 150 --upstream-root ../course-work")
        if not args.course_work_root: raise SystemExit("live release required: make evaluate COURSE_WORK_ROOT=../course-work")
    if not smoke and not args.require_real_data: raise SystemExit("use --allow-sample for smoke or --require-real-data with --course-work-root for release")
    try: raw, metrics = run(load_rows(), pathlib.Path(args.course_work_root) if args.course_work_root else None, smoke=smoke)
    except LiveRuntimeError as exc: raise SystemExit(f"live composition failed: {exc}") from exc
    metrics["dataset"] = manifest
    if upstream.exists():
        evidence = json.loads(upstream.read_text()); metrics["upstream_execution"] = {"weeks": len(evidence.get("weeks", [])), "rows_materialized": evidence.get("execution_rows", 0), "domains": sorted(x.get("domain") for x in evidence.get("weeks", []))}
    REPORTS.mkdir(exist_ok=True); (REPORTS / "results.jsonl").write_text("\n".join(json.dumps(row) for row in raw) + "\n")
    saved = dict(metrics); saved.pop("raw_results", None); (REPORTS / "metrics.json").write_text(json.dumps(saved, indent=2) + "\n")
    release_pass = bool(metrics["cases"] >= 150 and metrics["execution"]["mode"] == "live_coursework" and metrics.get("upstream_execution", {}).get("weeks") == 7 and all(r["execution_mode"] == "live_coursework" for r in raw) and all(r.get("components", {}).get("mcp", {}).get("live_execution") and r.get("components", {}).get("adaptation", {}).get("real_lora_complete") for r in raw) and metrics["observability"]["trace_count"] == metrics["cases"] and all(metrics["failure_matrix"][f]["cases"] > 0 for f in REQUIRED_FAILURES) and metrics["slo"]["latency_pass"] and metrics["slo"]["cost_pass"])
    report = {"schema_version": 3, "release_pass": release_pass, "checks": {"evaluation_cases": metrics["cases"], "execution_mode": metrics["execution"]["mode"], "live_components": metrics["execution"]["components"], "failure_boundaries": len(metrics["failure_matrix"]), "trace_count": metrics["observability"]["trace_count"], "slo": metrics["slo"]}, "metrics_file": "metrics.json"}; (REPORTS / "release_report.json").write_text(json.dumps(report, indent=2) + "\n")
    decision = "PASS" if release_pass else "CONDITIONAL"
    (REPORTS / "final_report.md").write_text(f"""# Week 8 release defense

## Decision

{decision} — derived from live component results in `results.jsonl`.

## Evidence

- Cases: {metrics['cases']}
- Runtime: {metrics['execution']['mode']}
- Components: {', '.join(metrics['execution']['components'])}
- Latency p95 (ms): {metrics['latency_p95_ms']:.3f}
- Cost per successful task (USD): {metrics['cost_per_successful_task']:.6f}
- Failure boundaries exercised: {len(metrics['failure_matrix'])}

## Limits

Smoke mode is intentionally non-promotable. A release is valid only when this runner invokes the Week 2 retrieval, Week 3 MCP boundary, Week 4 planner-executor, Week 5 policy boundary, Week 6 strict PEFT adapter, and Week 7 durable telemetry workflow from the supplied course-work directory. Provider-backed model quality remains a separate production experiment.
""")
    print(json.dumps({"week": 8, "mode": metrics["execution"]["mode"], "cases": metrics["cases"], "release_pass": release_pass}))


if __name__ == "__main__": main()
