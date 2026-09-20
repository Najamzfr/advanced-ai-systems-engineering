# Week 4 — Planner–Executor–Verifier

Build a multi-step evidence assistant over a pinned public-document corpus. The
runtime is offline and deterministic so that every number can be reproduced.
It implements a dependency-aware planner, an executor with bounded retries, a
verifier that checks citations and answer support, and equal-budget baselines.

```bash
make setup                 # materialise the pinned corpus and 25 cases
make run                   # plan, execute, verify, and write reports/
make grade                 # strict local grading
make check-step-1          # each of the 12 checkpoint checks
```

The corpus is adapted from the Python documentation (URLs are retained in the
manifest). A learner may replace `data/eval.jsonl` with a larger approved
export, but must preserve `case_id`, `question`, `gold_evidence`, and `steps`.
No model call is required: the planning and evidence contracts are the skill
being measured. Provider-backed experiments can be added after the deterministic
baseline is passing.

## Runtime interface for later builds

Later weeks call the same runtime rather than replaying this week's reports:

```bash
python agent_runtime.py --question "How do Python virtual environments work?" \
  --request-id demo-001 --failure-mode tool_timeout
```

Python callers can import `execute_request(question, request_id, failure_mode)`
from `agent_runtime.py`. It returns the plan, bounded execution, verification,
live-execution flag, and request ID.

When continuing from Week 2, reuse its frozen QASPER snapshot:

```bash
python scripts/fetch_data.py --cases 25 --from-week2 ../week-2-project
```
