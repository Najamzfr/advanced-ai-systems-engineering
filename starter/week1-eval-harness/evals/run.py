import argparse
import json
from pathlib import Path

from .metrics import judge_agreement, summarize
from .providers import available_models, predict

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
            rows.append({**case, "model": model, "prediction": result["label"], "schema_valid": result["schema_valid"], "latency_ms": result["latency_ms"]})
        predictions.extend(rows)
        summaries[model] = summarize(rows)
    (out_dir / "predictions.jsonl").write_text("\n".join(json.dumps(row) for row in predictions) + "\n")
    audit_path = ROOT / "data" / "judge_audit.jsonl"
    audit = load_jsonl(audit_path) if audit_path.exists() else []
    metrics = {"dataset": data_mode, "models": summaries, "judge_agreement": judge_agreement(audit), "judge_denominator": len(audit)}
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
