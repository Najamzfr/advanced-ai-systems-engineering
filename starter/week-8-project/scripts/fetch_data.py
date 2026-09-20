"""Materialize Week 8 from Weeks 1--7 raw evidence.

The release workload is made from prior projects' ``reports/results.jsonl``
rows. Aggregate metrics remain provenance, but are never treated as execution.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FAILURES = ["none", "none", "none", "model_unavailable", "retrieval_down", "tool_timeout", "database_timeout", "approval_timeout"]
UPSTREAM = {
    1: ("week1-eval-harness", ("metrics.json", "results.jsonl", "grade.json"), "evaluation"),
    2: ("week-2-project", ("metrics.json", "results.jsonl"), "retrieval"),
    3: ("week-3-project", ("metrics.json", "results.jsonl"), "tools"),
    4: ("week-4-project", ("metrics.json", "results.jsonl"), "planning"),
    5: ("week-5-project", ("metrics.json", "results.jsonl"), "security"),
    6: ("week-6-project", ("metrics.json", "results.jsonl", "adaptation_report.json", "leakage.json"), "adaptation"),
    7: ("week-7-project", ("metrics.json", "results.jsonl", "telemetry.ndjson"), "observability"),
}

def read_jsonl(path):
    rows = []
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip(): continue
        try: rows.append(json.loads(line))
        except json.JSONDecodeError as exc: raise SystemExit(f"invalid JSON in {path} line {line_no}: {exc}")
    return rows

def source_row(week, row, index):
    case_id = row.get("case_id") or row.get("run_id") or row.get("question_id") or f"row-{index + 1}"
    question = row.get("question") or row.get("prompt") or row.get("query") or row.get("task") or f"Replay Week {week} upstream case {case_id}."
    success = row.get("success", row.get("completed", row.get("regression_pass", True)))
    expected = "completed" if success else "bounded_failure"
    risk = "high" if row.get("kind") == "attack" or row.get("risk") == "high" else "medium" if week in (5, 7) else "low"
    canonical = json.dumps(row, sort_keys=True, default=str).encode()
    return {"case_id": f"w{week}-{case_id}", "question": str(question), "expected": expected,
            "failure": "none", "risk": risk, "source_week": week,
            "source_case_id": str(case_id), "source_sha256": hashlib.sha256(canonical).hexdigest()}

def materialize_upstream(root, requested_cases):
    evidence, candidates = [], []
    for week, (dirname, required, domain) in UPSTREAM.items():
        report_root = root / dirname / "reports"
        missing = [name for name in required if not (report_root / name).exists()]
        if missing: raise SystemExit(f"upstream Week {week} missing required artifacts: {', '.join(missing)}")
        try: metrics = json.loads((report_root / "metrics.json").read_text())
        except json.JSONDecodeError as exc: raise SystemExit(f"invalid upstream Week {week} metrics.json: {exc}")
        raw_path = report_root / "results.jsonl"; raw_rows = read_jsonl(raw_path)
        if not raw_rows: raise SystemExit(f"upstream Week {week} has no raw rows in {raw_path}")
        artifacts = {}
        for name in required:
            path = report_root / name
            artifacts[name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
        evidence.append({"week": week, "domain": domain, "project": dirname, "metrics": metrics,
                         "raw_case_count": len(raw_rows), "artifacts": artifacts})
        candidates.extend(source_row(week, row, i) for i, row in enumerate(raw_rows))
    if len(candidates) < requested_cases:
        raise SystemExit(f"upstream raw evidence provides {len(candidates)} rows; need at least {requested_cases}")
    by_week = {week: [r for r in candidates if r["source_week"] == week] for week in UPSTREAM}
    rows = []
    while len(rows) < requested_cases:
        progressed = False
        for week in UPSTREAM:
            if by_week[week] and len(rows) < requested_cases:
                row = by_week[week].pop(0); row["failure"] = FAILURES[len(rows) % len(FAILURES)]
                rows.append(row); progressed = True
        if not progressed: break
    return rows, evidence

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cases", type=int, default=150); ap.add_argument("--upstream-root", type=pathlib.Path); args = ap.parse_args()
    if args.cases < 20: raise SystemExit("--cases must be at least 20")
    if args.cases >= 150 and not args.upstream_root: raise SystemExit("--upstream-root is required for a release pack (150+ cases); smoke uses make run")
    rows, upstream = materialize_upstream(args.upstream_root, args.cases) if args.upstream_root else ([], [])
    payload = "\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n"; digest = hashlib.sha256(payload.encode()).hexdigest(); DATA.mkdir(exist_ok=True)
    if upstream:
        (DATA / "upstream-evidence.json").write_text(json.dumps({"source_root": str(args.upstream_root.resolve()), "weeks": upstream, "execution_rows": len(rows)}, indent=2) + "\n")
        (DATA / "release.jsonl").write_text(payload)
    (DATA / "manifest.json").write_text(json.dumps({"week": 8, "status": "materialized" if upstream else "smoke_fixture", "source_type": "upstream_raw_evidence" if upstream else "smoke_fixture", "source": "Weeks 1-7 reports/results.jsonl", "cases": len(rows), "sha256": digest, "minimum_cases_for_grade": 150, "upstream_evidence": bool(upstream), "required_upstream_weeks": 7}, indent=2) + "\n")
    print(json.dumps({"cases": len(rows), "source": "Weeks 1-7 raw evidence" if upstream else "smoke_fixture", "sha256": digest, "upstream_weeks": len(upstream)}))

if __name__ == "__main__": main()
