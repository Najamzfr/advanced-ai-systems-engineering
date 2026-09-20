import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_CONFUSION_INTENTS = [
    "card_arrival", "card_delivery_estimate", "pending_cash_withdrawal",
    "declined_cash_withdrawal", "cash_withdrawal_not_recognised",
    "cash_withdrawal_charge", "wrong_exchange_rate_for_cash_withdrawal",
    "pending_card_payment", "declined_card_payment",
    "card_payment_not_recognised", "reverted_card_payment",
    "pending_top_up", "top_up_reverted", "top_up_failed", "verify_top_up",
]


def evidence(passed, observed, required, message):
    return {"passed": bool(passed), "observed": observed, "required": required, "message": message}


def report_quality():
    path = ROOT / "reports/model_selection.md"
    if not path.exists():
        return evidence(False, "missing", "structured decision memo", "reports/model_selection.md is missing")
    text = path.read_text()
    lowered = text.lower()
    headings = ["decision", "evidence", "failure analysis", "judge calibration", "deployment recommendation", "limitations"]
    missing_headings = [h for h in headings if not re.search(rf"^##\s+{re.escape(h)}\s*$", lowered, re.MULTILINE)]
    terms = ["baseline-v1", "robust-v2", "macro f1", "schema validity", "latency p95", "cost per successful case", "judge agreement", "fallback"]
    missing_terms = [term for term in terms if term not in lowered]
    evidence_rows = [line for line in text.splitlines() if line.lstrip().startswith("|") and any(metric in line.lower() for metric in ("macro f1", "schema validity", "latency p95", "cost per successful case", "judge agreement"))]
    numeric_rows = 0
    for line in evidence_rows:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.search(r"\d", cells[1]) and re.search(r"\d", cells[2]):
            numeric_rows += 1
    word_count = len(re.findall(r"\b[\w'-]+\b", text))
    passed = not missing_headings and not missing_terms and numeric_rows == 5 and word_count >= 250
    observed = {"words": word_count, "metric_rows_with_numbers": numeric_rows, "missing_headings": missing_headings, "missing_terms": missing_terms}
    required = {"minimum_words": 250, "numeric_metric_rows": 5, "headings": headings, "terms": terms}
    return evidence(passed, observed, required, "deterministic structure and evidence check; human review still judges reasoning quality")


def check_setup():
    required = [ROOT / "data/manifest.json", ROOT / "data/sample.jsonl", ROOT / "evals/run.py", ROOT / "reports"]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise SystemExit("Missing starter paths: " + ", ".join(missing))
    print("setup: ready; smoke fixture available; real benchmark not claimed")


def check_grade():
    metrics_path = ROOT / "reports/metrics.json"
    manifest_path = ROOT / "data/manifest.json"
    errors = []
    eval_path = ROOT / "data/eval.jsonl"
    if not metrics_path.exists(): errors.append("reports/metrics.json is missing; run make evaluate")
    if not eval_path.exists(): errors.append("data/eval.jsonl is missing; fetch the real BANKING77 split")
    if errors:
        file_checks = {
            "metrics_file": evidence(metrics_path.exists(), "present" if metrics_path.exists() else "missing", "reports/metrics.json", "run make evaluate"),
            "evaluation_file": evidence(eval_path.exists(), "present" if eval_path.exists() else "missing", "data/eval.jsonl", "fetch the real BANKING77 split"),
        }
        (ROOT / "reports/grade.json").write_text(json.dumps({"status": "fail", "summary": {"passed": sum(v["passed"] for v in file_checks.values()), "total": len(file_checks)}, "checks": file_checks, "errors": errors}, indent=2) + "\n")
        raise SystemExit("GRADE FAIL\n- " + "\n- ".join(errors))
    metrics = json.loads(metrics_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    models = metrics.get("models", {})
    evidence_path = ROOT / "reports/results.jsonl"
    evidence_rows = []
    if evidence_path.exists():
        try:
            evidence_rows = [json.loads(line) for line in evidence_path.read_text().splitlines() if line.strip()]
        except json.JSONDecodeError:
            errors.append("reports/results.jsonl contains invalid JSON")
    expected_cases = manifest.get("cases", 0)
    evidence_models = {row.get("model") for row in evidence_rows}
    evidence_ids = {(row.get("model"), row.get("case_id")) for row in evidence_rows}
    evidence_checks = {
        "raw_evidence": evidence_path.exists() and len(evidence_rows) == expected_cases * 2 and evidence_models == {"baseline-v1", "robust-v2"},
        "unique_paired_cases": len(evidence_ids) == len(evidence_rows) and all(row.get("case_id") for row in evidence_rows),
        "derived_case_counts": all(values.get("cases") == sum(row.get("model") == model for row in evidence_rows) for model, values in models.items()),
    }
    audit_path = ROOT / "data/judge_audit.jsonl"
    audit_rows = []
    if audit_path.exists():
        try:
            audit_rows = [json.loads(line) for line in audit_path.read_text().splitlines() if line.strip()]
        except json.JSONDecodeError:
            errors.append("data/judge_audit.jsonl contains invalid JSON")
    robust_by_case = {row.get("case_id"): row for row in evidence_rows if row.get("model") == "robust-v2"}
    audit_required_fields = {"case_id", "gold_label", "model_label", "judge_label", "agree", "reviewed_by", "reviewed_at", "review_note"}
    audit_ids = [row.get("case_id") for row in audit_rows]
    audit_valid = bool(audit_rows) and len(audit_ids) == len(set(audit_ids)) and all(audit_required_fields <= set(row) for row in audit_rows)
    audit_valid = audit_valid and all(
        row.get("case_id") in robust_by_case
        and row.get("gold_label") == robust_by_case[row["case_id"]].get("label")
        and row.get("model_label") == robust_by_case[row["case_id"]].get("prediction")
        and isinstance(row.get("agree"), bool)
        and row.get("agree") == (row.get("judge_label") == row.get("gold_label"))
        and str(row.get("reviewed_by", "")).strip()
        and str(row.get("reviewed_at", "")).strip()
        and str(row.get("review_note", "")).strip()
        for row in audit_rows
    )
    model_names = sorted(models)
    intent_counts = {}
    for model, values in models.items():
        per_intent = values.get("per_intent", {})
        intent_counts[model] = {intent: per_intent.get(intent, {}).get("cases", 0) for intent in REQUIRED_CONFUSION_INTENTS}
    intent_observed = {model: {"minimum_count": min(counts.values(), default=0), "missing_or_short": [intent for intent, count in counts.items() if count < 15]} for model, counts in intent_counts.items()}
    intent_pass = set(models) == {"baseline-v1", "robust-v2"} and all(not values["missing_or_short"] for values in intent_observed.values())
    checks = {
        "raw_evidence": evidence(evidence_checks["raw_evidence"], len(evidence_rows), expected_cases * 2, "reports/results.jsonl must contain one row per model and frozen case"),
        "paired_evidence_ids": evidence(evidence_checks["unique_paired_cases"], len(evidence_ids), len(evidence_rows), "raw case IDs must be unique within each model"),
        "metrics_derived_from_evidence": evidence(evidence_checks["derived_case_counts"], {k: v.get("cases") for k, v in models.items()}, "counts must match raw evidence", "reported case counts cannot be fabricated"),
        "real_data": evidence(manifest.get("status") == "real_data", manifest.get("status"), "real_data", "use the downloaded BANKING77 split"),
        "minimum_cases": evidence(manifest.get("cases", 0) >= 300, manifest.get("cases", 0), ">= 300", "frozen evaluation cases"),
        "paired_models": evidence(set(models) == {"baseline-v1", "robust-v2"}, model_names, ["baseline-v1", "robust-v2"], "evaluate both configurations"),
        "paired_case_counts": evidence(all(v.get("cases", 0) >= 300 for v in models.values()) and len(models) == 2, {k: v.get("cases", 0) for k, v in models.items()}, ">= 300 per model", "same frozen cases for both models"),
        "schema_validity": evidence(all(v.get("schema_validity", 0) == 1 for v in models.values()) and len(models) == 2, {k: v.get("schema_validity", 0) for k, v in models.items()}, "1.0 per model", "all structured outputs must validate"),
        "confusion_intent_coverage": evidence(intent_pass, intent_observed, {"minimum_each": 15, "intents": REQUIRED_CONFUSION_INTENTS}, "fixed confusion-prone BANKING77 slice"),
        "judge_audit": evidence(metrics.get("judge_denominator", 0) >= 30 and len(audit_rows) == metrics.get("judge_denominator", 0) and audit_valid, {"metric_denominator": metrics.get("judge_denominator", 0), "valid_rows": len(audit_rows) if audit_valid else 0}, ">= 30 linked, adjudicated rows", "audit rows must be linked to robust-v2 evidence and include reviewer, timestamp, and note"),
        "model_selection_report": report_quality(),
    }
    for name, item in checks.items():
        if not item["passed"]:
            errors.append(f"{name}: {item['message']}")
    result = {
        "status": "pass" if not errors else "fail",
        "summary": {"passed": sum(item["passed"] for item in checks.values()), "total": len(checks)},
        "checks": checks,
        "errors": errors,
    }
    (ROOT / "reports/grade.json").write_text(json.dumps(result, indent=2) + "\n")
    if errors:
        raise SystemExit("GRADE FAIL\n- " + "\n- ".join(errors) + "\nMachine-readable result: reports/grade.json")
    print("GRADE PASS\n- real BANKING77 data\n- 300+ paired cases\n- fixed 15-intent confusion slice\n- two model configurations\n- 30+ judge audit rows\n- structured model-selection memo\nMachine-readable result: reports/grade.json")


def _load_metrics():
    path = ROOT / "reports/metrics.json"
    if not path.exists():
        raise SystemExit("STEP FAIL\n- reports/metrics.json is missing; run make run or make evaluate")
    return json.loads(path.read_text())


def check_step(step):
    if step < 1 or step > 12:
        raise SystemExit("step must be between 1 and 12")
    metrics = _load_metrics()
    models = metrics.get("models", {})
    manifest = json.loads((ROOT / "data/manifest.json").read_text())
    errors = []
    if step == 1:
        required = {"baseline-v1", "robust-v2"}
        if set(models) != required:
            errors.append("models must contain exactly baseline-v1 and robust-v2")
        if metrics.get("dataset") not in {"smoke_fixture", "banking77"}:
            errors.append("dataset must be smoke_fixture or banking77")
        if not all("denominator" in v for v in models.values()):
            errors.append("each model needs a denominator object")
        label = "starter contract and smoke metrics"
    elif step == 2:
        if not all(v.get("cases", 0) == 3 for v in models.values()): errors.append("smoke run must report three cases per model")
        label = "equal smoke denominators"
    elif step == 3:
        if not (ROOT / "reports/predictions.jsonl").exists(): errors.append("reports/predictions.jsonl is missing")
        if not (ROOT / "reports/results.jsonl").exists(): errors.append("reports/results.jsonl is missing")
        else:
            rows = [json.loads(line) for line in (ROOT / "reports/results.jsonl").read_text().splitlines() if line.strip()]
            if len(rows) != sum(v.get("cases", 0) for v in models.values()): errors.append("raw results count must equal reported model case counts")
        label = "raw provider results preserved"
    elif step == 4:
        if manifest.get("status") != "real_data": errors.append("data/manifest.json status must be real_data")
        if manifest.get("cases", 0) < 300: errors.append("manifest cases must be at least 300")
        if metrics.get("dataset") != "banking77": errors.append("metrics dataset must be banking77")
        if any(v.get("cases", 0) < 300 for v in models.values()): errors.append("both models need 300+ cases")
        for model, values in models.items():
            per_intent = values.get("per_intent", {})
            missing = [intent for intent in REQUIRED_CONFUSION_INTENTS if per_intent.get(intent, {}).get("cases", 0) < 15]
            if missing: errors.append(f"{model} is missing 15+ cases for: {', '.join(missing)}")
        label = "paired real-data evaluation and per-intent coverage"
    elif step == 7:
        if any(set(v.get("denominator", {})) < {"quality", "schema", "latency"} for v in models.values()): errors.append("quality, schema and latency denominators are required")
        label = "quality, schema and latency denominators"
    elif step == 8:
        if not (ROOT / "tests/test_contracts.py").exists(): errors.append("tests/test_contracts.py is missing")
        label = "contract test files present"
    elif step == 9:
        if not (ROOT / "reports/results.jsonl").exists(): errors.append("raw results are missing")
        else:
            rows = [json.loads(line) for line in (ROOT / "reports/results.jsonl").read_text().splitlines() if line.strip()]
            if len({(row.get("model"), row.get("case_id")) for row in rows}) != len(rows): errors.append("raw evidence has duplicate model/case pairs")
            if any(not all(key in row for key in ("model", "case_id", "label", "prediction", "latency_ms", "provider")) for row in rows): errors.append("raw evidence rows are missing provider fields")
        label = "raw failure evidence present"
    elif step == 10:
        audit_path = ROOT / "data/judge_audit.jsonl"
        audit_required = {"case_id", "gold_label", "model_label", "judge_label", "agree", "reviewed_by", "reviewed_at", "review_note"}
        try:
            audit_rows = [json.loads(line) for line in audit_path.read_text().splitlines() if line.strip()] if audit_path.exists() else []
        except json.JSONDecodeError:
            audit_rows = []
        if metrics.get("judge_denominator", 0) < 30 or len(audit_rows) != metrics.get("judge_denominator", 0): errors.append("judge audit must contain at least 30 rows and match judge_denominator")
        if len({row.get("case_id") for row in audit_rows}) != len(audit_rows): errors.append("judge audit case_id values must be unique")
        if not all(audit_required <= set(row) and str(row.get("reviewed_by", "")).strip() and str(row.get("reviewed_at", "")).strip() and str(row.get("review_note", "")).strip() for row in audit_rows): errors.append("judge audit rows need reviewer, timestamp, note, and adjudication fields")
        label = "linked human judge audit evidence"
    elif step == 11:
        report = report_quality()
        if not report["passed"]: errors.append("model_selection.md fails the deterministic structure/evidence contract")
        label = "model-selection report quality"
    else:
        report = report_quality()
        if metrics.get("judge_denominator", 0) < 30: errors.append("judge_denominator must be at least 30")
        if not report["passed"]: errors.append("model_selection.md fails the deterministic structure/evidence contract")
        label = "release decision and limitations"
    if step in {5, 6}:
        if metrics.get("dataset") != "banking77": errors.append("metrics dataset must be banking77")
        if any(v.get("cases", 0) < 300 for v in models.values()): errors.append("both models need 300+ cases")
        if step == 5: label = "paired model case counts"
        else: label = "fixed confusion-intent coverage"
        for model, values in models.items():
            per_intent = values.get("per_intent", {})
            missing = [intent for intent in REQUIRED_CONFUSION_INTENTS if per_intent.get(intent, {}).get("cases", 0) < 15]
            if step == 6 and missing: errors.append(f"{model} is missing 15+ cases for: {', '.join(missing)}")
    if step == 6:
        for model, values in models.items():
            per_intent = values.get("per_intent", {})
            missing = [intent for intent in REQUIRED_CONFUSION_INTENTS if per_intent.get(intent, {}).get("cases", 0) < 15]
            if missing: errors.append(f"{model} lacks the fixed confusion-intent coverage")
    if step == 12:
        if not (ROOT / "reports/grade.json").exists(): errors.append("reports/grade.json is missing; run make grade")
    if errors:
        print("STEP FAIL")
        for error in errors: print(f"- {error}")
        raise SystemExit(1)
    print(f"STEP PASS {step}: {label}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["setup", "grade"] + [f"check-step-{n}" for n in range(1, 13)])
    args = parser.parse_args()
    if args.command == "setup": check_setup()
    elif args.command == "grade": check_grade()
    else: check_step(int(args.command.rsplit("-", 1)[1]))


if __name__ == "__main__":
    main()
