import argparse
import json
import os
from pathlib import Path

from .metrics import judge_agreement, summarize
from .providers import available_models, predict
from .judge import judge_case

ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-sample", action="store_true")
    parser.add_argument("--require-real-data", action="store_true")
    args = parser.parse_args()
    real_path = ROOT / "data" / "eval.jsonl"
    sample_path = ROOT / "data" / "sample.jsonl"
    if real_path.exists():
        cases = load_jsonl(real_path)
        data_mode = "banking77"
    elif args.allow_sample and not args.require_real_data:
        cases = load_jsonl(sample_path)
        data_mode = "smoke_fixture"
    else:
        raise SystemExit("No data/eval.jsonl found. Run: python scripts/fetch_banking77.py --cases 300 --min-per-intent 15")

    out_dir = ROOT / "reports"
    out_dir.mkdir(exist_ok=True)
    predictions = []
    summaries = {}
    for model in available_models():
        rows = []
        for case in cases:
            result = predict(model, case["text"])
            provider_result = {key: value for key, value in result.items() if key != "label"}
            rows.append({**case, "model": model, "prediction": result["label"], **provider_result})
        predictions.extend(rows)
        summaries[model] = summarize(rows)
    (out_dir / "predictions.jsonl").write_text("\n".join(json.dumps(row) for row in predictions) + "\n")
    (out_dir / "results.jsonl").write_text("\n".join(json.dumps(row) for row in predictions) + "\n")
    audit_path = ROOT / "data" / "judge_audit.jsonl"
    audit = load_jsonl(audit_path) if audit_path.exists() else []
    review_queue = []
    for case in cases[:30]:
        prediction = next((row["prediction"] for row in predictions if row["model"] == "robust-v2" and row["case_id"] == case["case_id"]), "unknown")
        review_queue.append({"case_id": case["case_id"], "text": case["text"], "gold_label": case["label"], "model_label": prediction, **judge_case(case, prediction), "model": "robust-v2", "reviewed_by": "", "reviewed_at": "", "review_note": "", "review_status": "needs_human_review"})
    (out_dir / "judge_review_queue.jsonl").write_text("\n".join(json.dumps(row) for row in review_queue) + "\n")
    provider_modes = sorted({row.get("provider", "unknown") for row in predictions})
    metrics = {"dataset": data_mode, "models": summaries, "judge_agreement": judge_agreement(audit), "judge_denominator": len(audit), "judge": {"prompt": "evals/judge.py:JUDGE_PROMPT", "mode": os.getenv("WEEK1_JUDGE", "offline"), "audit_source": str(audit_path.relative_to(ROOT)), "review_queue": "reports/judge_review_queue.jsonl", "human_review_required": True}, "provider_modes": provider_modes}
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
