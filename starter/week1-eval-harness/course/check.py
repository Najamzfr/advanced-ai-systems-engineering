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
    model_names = sorted(models)
    intent_counts = {}
    for model, values in models.items():
        per_intent = values.get("per_intent", {})
        intent_counts[model] = {intent: per_intent.get(intent, {}).get("cases", 0) for intent in REQUIRED_CONFUSION_INTENTS}
    intent_observed = {model: {"minimum_count": min(counts.values(), default=0), "missing_or_short": [intent for intent, count in counts.items() if count < 15]} for model, counts in intent_counts.items()}
    intent_pass = set(models) == {"baseline-v1", "robust-v2"} and all(not values["missing_or_short"] for values in intent_observed.values())
    checks = {
        "real_data": evidence(manifest.get("status") == "real_data", manifest.get("status"), "real_data", "use the downloaded BANKING77 split"),
        "minimum_cases": evidence(manifest.get("cases", 0) >= 300, manifest.get("cases", 0), ">= 300", "frozen evaluation cases"),
        "paired_models": evidence(set(models) == {"baseline-v1", "robust-v2"}, model_names, ["baseline-v1", "robust-v2"], "evaluate both configurations"),
        "paired_case_counts": evidence(all(v.get("cases", 0) >= 300 for v in models.values()) and len(models) == 2, {k: v.get("cases", 0) for k, v in models.items()}, ">= 300 per model", "same frozen cases for both models"),
        "schema_validity": evidence(all(v.get("schema_validity", 0) == 1 for v in models.values()) and len(models) == 2, {k: v.get("schema_validity", 0) for k, v in models.items()}, "1.0 per model", "all structured outputs must validate"),
        "confusion_intent_coverage": evidence(intent_pass, intent_observed, {"minimum_each": 15, "intents": REQUIRED_CONFUSION_INTENTS}, "fixed confusion-prone BANKING77 slice"),
        "judge_audit": evidence(metrics.get("judge_denominator", 0) >= 30, metrics.get("judge_denominator", 0), ">= 30", "human-reviewed judge calibration rows"),
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
    checkpoint = (step - 1) // 3 + 1
    substep = (step - 1) % 3 + 1
    step = checkpoint
    metrics = _load_metrics()
    models = metrics.get("models", {})
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
        manifest = json.loads((ROOT / "data/manifest.json").read_text())
        if manifest.get("status") != "real_data": errors.append("data/manifest.json status must be real_data")
        if manifest.get("cases", 0) < 300: errors.append("manifest cases must be at least 300")
        if metrics.get("dataset") != "banking77": errors.append("metrics dataset must be banking77")
        if any(v.get("cases", 0) < 300 for v in models.values()): errors.append("both models need 300+ cases")
        for model, values in models.items():
            per_intent = values.get("per_intent", {})
            missing = [intent for intent in REQUIRED_CONFUSION_INTENTS if per_intent.get(intent, {}).get("cases", 0) < 15]
            if missing: errors.append(f"{model} is missing 15+ cases for: {', '.join(missing)}")
        label = "paired real-data evaluation and per-intent coverage"
    elif step == 3:
        if any(set(v.get("denominator", {})) < {"quality", "schema", "latency"} for v in models.values()): errors.append("quality, schema and latency denominators are required")
        for model, values in models.items():
            per_intent = values.get("per_intent", {})
            missing = [intent for intent in REQUIRED_CONFUSION_INTENTS if per_intent.get(intent, {}).get("cases", 0) < 15]
            if missing: errors.append(f"{model} lacks the fixed confusion-intent coverage")
        if not (ROOT / "tests/test_contracts.py").exists(): errors.append("tests/test_contracts.py is missing")
        label = "complete metric denominators and contract coverage"
    else:
        if metrics.get("judge_denominator", 0) < 30: errors.append("judge_denominator must be at least 30")
        report = report_quality()
        if not report["passed"]: errors.append("model_selection.md fails the deterministic structure/evidence contract")
        label = "calibrated judge evidence and model-selection report"
    if errors:
        print("STEP FAIL")
        for error in errors: print(f"- {error}")
        raise SystemExit(1)
    print(f"STEP PASS {((checkpoint - 1) * 3) + substep}: {label} (sub-step {substep})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["setup", "grade"] + [f"check-step-{n}" for n in range(1, 13)])
    args = parser.parse_args()
    if args.command == "setup": check_setup()
    elif args.command == "grade": check_grade()
    else: check_step(int(args.command.rsplit("-", 1)[1]))


if __name__ == "__main__":
    main()
