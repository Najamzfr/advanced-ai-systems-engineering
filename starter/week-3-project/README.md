# Week 3 · Bounded tool-using agent

This starter runs immediately with a deterministic smoke fixture. The smoke
run verifies the project contract; it is not evidence for the real assignment.

```text
make setup
make run
make test
```

Then fetch the assigned data and run the real check:

```text
python scripts/fetch_data.py --cases 20
make evaluate
make grade
```

The grader requires `data/eval.jsonl`, the declared minimum case count and a
manifest marked `real_data`. It writes `reports/grade.json` so the course page
can display the result without guessing from checkboxes.

Dataset: Open-Meteo responses plus Week 2 evidence fixtures  
Source: https://api.open-meteo.com/v1/forecast  
Minimum real cases: 20  
Required artifact: `reports/agent_decision.md`

Required measurements: tool-selection accuracy, argument validity, successful completion rate, retry rate, duplicate-effect rate

The starter exposes `make check-step-1` through `make check-step-12`. Each
target reads `reports/metrics.json` and reports observed versus required
values. `make grade` writes structured `reports/grade.json` evidence for the
course importer.

The included provider/runtime is intentionally small and deterministic. Extend
it with the week’s actual system, preserve raw evidence, and document failures
before claiming success.
