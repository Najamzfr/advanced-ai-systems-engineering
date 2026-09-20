# Week 1 · Model evaluation harness

This starter is a small, dependency-free evaluation project. It gives you a
deterministic smoke run immediately, then asks you to fetch the licensed
BANKING77 records before claiming benchmark results.

## Quick start

```text
make setup
make run
```

The first run uses `data/sample.jsonl` and proves that the project wiring,
provider contract and report shape work. It is deliberately not a quality
benchmark.

## Build the real benchmark

```text
python scripts/fetch_banking77.py --cases 300 --min-per-intent 15
make evaluate
make grade
```

The fetch script records the source URL, split, row count and SHA-256 checksum
in `data/manifest.json`. It always includes the course's named 15-intent
confusion slice with at least 15 cases per intent. The local grader refuses to
pass a submission that only uses the smoke fixture or substitutes easier
intents. BANKING77's source CSV contains the historical label
`reverted_card_payment?`; the fetcher maps it to the learner-facing canonical
label `reverted_card_payment` before writing the evaluation split.

## What you will change

1. Add or replace provider adapters in `evals/providers.py`.
2. Keep both models on the same frozen case IDs.
3. Add 30 adjudicated rows to `data/judge_audit.jsonl`.
4. Explain the quality/latency/cost decision in `reports/model_selection.md`.

The report is checked deterministically for its required sections, both model
names, five populated metric rows, fallback, judge calibration, deployment
recommendation and at least 250 words. This verifies completeness, not the
quality of the reasoning; review that manually.

The included providers are deterministic baselines. They make the first run
repeatable; they are not presented as production model quality.

## Outputs

```text
reports/metrics.json
reports/predictions.jsonl
reports/model_selection.md
```

The metric file includes case count, macro-F1, schema validity, p95 latency,
cost per successful case and judge agreement. Every metric carries its
denominator and source configuration.

Each run also writes `reports/judge_review_queue.jsonl`, containing 30 rows
scored with the prompt in `evals/judge.py`. Treat it as a review queue: inspect
each row, correct the judge label when needed, then save it as
`data/judge_audit.jsonl` with `gold_label`, `model_label`, `judge_label`,
`agree`, `reviewed_by`, `reviewed_at`, and a non-empty `review_note`. The
grader links every audit row back to the recorded `robust-v2` prediction; it
counts only this human-reviewed file, never the automatically generated queue.

When you use an OpenAI-compatible provider, set the input/output price
assumptions through `WEEK1_INPUT_COST_PER_1K_USD` and
`WEEK1_OUTPUT_COST_PER_1K_USD`. The harness records that cost basis with every
raw result; it does not invent provider billing data.

BANKING77 is attributed to PolyAI and distributed under CC BY 4.0. Check the
source terms before redistributing the downloaded records.
