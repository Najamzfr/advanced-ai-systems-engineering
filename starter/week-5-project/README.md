# Week 5 · Red-team and repair the agent

This starter runs immediately with a deterministic smoke fixture. The smoke
run verifies the project contract; it is not evidence for the real assignment.

```text
make setup
make run
make test
```

Then fetch the assigned data and run the real check:

```text
python scripts/fetch_data.py --cases 50
make evaluate
make grade
```

The grader requires `data/eval.jsonl`, the declared minimum case count and a
manifest marked `real_data`. It writes `reports/grade.json` so the course page
can display the result without guessing from checkboxes.

Dataset: Course-owned fixed attack pack with benign controls  
Source: local:security/attacks.jsonl  
Minimum real cases: 50  
Required artifact: `reports/red_team_report.json`

Required measurements: attack success rate, benign task success, unauthorized tool-call rate, false refusal rate, recovery rate

The starter exposes `make check-step-1` through `make check-step-12`. Each
target reads `reports/metrics.json` and reports observed versus required
values. `make grade` writes structured `reports/grade.json` evidence for the
course importer.

The included provider/runtime is intentionally small and deterministic. Extend
it with the week’s actual system, preserve raw evidence, and document failures
before claiming success.
