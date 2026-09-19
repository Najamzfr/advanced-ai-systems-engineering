from collections import defaultdict


def macro_f1(rows):
    labels = sorted({r["label"] for r in rows} | {r["prediction"] for r in rows})
    values = []
    for label in labels:
        tp = sum(r["label"] == label and r["prediction"] == label for r in rows)
        fp = sum(r["label"] != label and r["prediction"] == label for r in rows)
        fn = sum(r["label"] == label and r["prediction"] != label for r in rows)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        values.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return round(sum(values) / len(values), 6) if values else 0.0


def summarize(rows):
    latencies = sorted(r["latency_ms"] for r in rows)
    p95_index = max(0, min(len(latencies) - 1, int(0.95 * len(latencies) + 0.999) - 1))
    per_intent = {}
    for label in sorted({r["label"] for r in rows}):
        subset = [r for r in rows if r["label"] == label]
        per_intent[label] = {
            "cases": len(subset),
            "correct": sum(r["label"] == r["prediction"] for r in subset),
            "recall": round(sum(r["label"] == r["prediction"] for r in subset) / len(subset), 6),
        }
    return {
        "cases": len(rows),
        "macro_f1": macro_f1(rows),
        "schema_validity": round(sum(r["schema_valid"] for r in rows) / len(rows), 6) if rows else 0.0,
        "latency_p95_ms": latencies[p95_index] if latencies else None,
        "cost_per_successful_case_usd": 0.0,
        "per_intent": per_intent,
        "denominator": {"quality": len(rows), "schema": len(rows), "latency": len(rows)},
    }


def judge_agreement(rows):
    if not rows:
        return None
    return round(sum(bool(r.get("agree")) for r in rows) / len(rows), 6)
