# Week 4 · Planner-executor research release

This starter runs immediately with a deterministic smoke fixture. The smoke
run verifies the project contract; it is not evidence for the real assignment.

```text
make setup
make run
make test
```

Then fetch the assigned data and run the real check:

```text
python scripts/fetch_data.py --cases 25
make evaluate
make grade
```

The grader requires `data/eval.jsonl`, the declared minimum case count and a
manifest marked `real_data`. It writes `reports/grade.json` so the course page
can display the result without guessing from checkboxes.

Dataset: Held-out multi-hop questions from the Week 2 manifest  
Source: local:week-2-eval.jsonl  
Minimum real cases: 25  
Required artifact: `reports/architecture_decision.md`

Required measurements: task success, evidence completeness, unsupported-claim rate, model calls, token use, p95 latency

The starter exposes `make check-step-1` through `make check-step-12`. Each
target reads `reports/metrics.json` and reports observed versus required
values. `make grade` writes structured `reports/grade.json` evidence for the
course importer.

The included provider/runtime is intentionally small and deterministic. Extend
it with the week’s actual system, preserve raw evidence, and document failures
before claiming success.
