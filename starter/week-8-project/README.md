# Week 8 · Deploy, monitor and defend the system

This starter runs immediately with a deterministic smoke fixture. The smoke
run verifies the project contract; it is not evidence for the real assignment.

```text
make setup
make run
make test
```

Then fetch the assigned data and run the real check:

```text
python scripts/fetch_data.py --cases 150
make evaluate
make grade
```

The grader requires `data/eval.jsonl`, the declared minimum case count and a
manifest marked `real_data`. It writes `reports/grade.json` so the course page
can display the result without guessing from checkboxes.

Dataset: Full evaluation, security and recovery packs  
Source: local:course-release-manifest.json  
Minimum real cases: 150  
Required artifact: `reports/release_report.json`

Required measurements: release pass rate, quality under failure, recovery success, SLO compliance, cost per successful task, open limitations

The starter exposes `make check-step-1` through `make check-step-12`. Each
target reads `reports/metrics.json` and reports observed versus required
values. `make grade` writes structured `reports/grade.json` evidence for the
course importer.

The included provider/runtime is intentionally small and deterministic. Extend
it with the week’s actual system, preserve raw evidence, and document failures
before claiming success.
