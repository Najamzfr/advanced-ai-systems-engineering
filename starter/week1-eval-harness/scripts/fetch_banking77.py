import argparse
import csv
import hashlib
import json
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/train.csv"
REQUIRED_CONFUSION_INTENTS = [
    "card_arrival",
    "card_delivery_estimate",
    "pending_cash_withdrawal",
    "declined_cash_withdrawal",
    "cash_withdrawal_not_recognised",
    "cash_withdrawal_charge",
    "wrong_exchange_rate_for_cash_withdrawal",
    "pending_card_payment",
    "declined_card_payment",
    "card_payment_not_recognised",
    "reverted_card_payment",
    "pending_top_up",
    "top_up_reverted",
    "top_up_failed",
    "verify_top_up",
]
SOURCE_INTENT_ALIASES = {"reverted_card_payment?": "reverted_card_payment"}

def canonical_intent(label):
    """Normalize the historical BANKING77 punctuation variant once at ingest."""
    return label.strip().rstrip("?")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=int, default=300)
    parser.add_argument("--min-per-intent", type=int, default=15)
    parser.add_argument("--url", default=DEFAULT_URL)
    args = parser.parse_args()
    raw = urllib.request.urlopen(args.url, timeout=60).read()
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    text_key = "text" if "text" in rows[0] else "query"
    label_key = "category" if "category" in rows[0] else "label"
    buckets = defaultdict(list)
    for row in rows:
        buckets[canonical_intent(row[label_key])].append(row[text_key])
    missing = [label for label in REQUIRED_CONFUSION_INTENTS if label not in buckets]
    if missing:
        raise SystemExit("BANKING77 source is missing required confusion intents: " + ", ".join(missing))
    selected = []
    ordered_labels = REQUIRED_CONFUSION_INTENTS + [
        label for label in sorted(buckets) if label not in REQUIRED_CONFUSION_INTENTS
    ]
    for label in ordered_labels:
        for text in buckets[label][: args.min_per_intent]:
            selected.append({"case_id": f"banking77-{len(selected)+1:04d}", "text": text, "label": label})
    if len(selected) < args.cases:
        raise SystemExit(f"Source only yielded {len(selected)} cases at the requested per-intent floor")
    selected = selected[: args.cases]
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "eval.jsonl").write_text("\n".join(json.dumps(row) for row in selected) + "\n")
    digest = hashlib.sha256((data_dir / "eval.jsonl").read_bytes()).hexdigest()
    intent_counts = {label: sum(row["label"] == label for row in selected) for label in REQUIRED_CONFUSION_INTENTS}
    manifest = {"dataset": "BANKING77", "source": args.url, "license": "CC BY 4.0", "split": "train", "status": "real_data", "cases": len(selected), "sha256": digest, "minimum_cases_for_grade": 300, "minimum_cases_per_intent": args.min_per_intent, "required_confusion_intents": REQUIRED_CONFUSION_INTENTS, "source_intent_aliases": SOURCE_INTENT_ALIASES, "canonicalization": "strip trailing '?' from historical source labels", "required_intent_counts": intent_counts}
    (data_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
