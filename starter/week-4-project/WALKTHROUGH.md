# Checkpoint 1 walkthrough

1. Run `make setup`. The command writes 24 uniquely identified questions and a
   manifest linking the eight source documents to Python documentation URLs.
2. Run `make run`. The planner turns each question into dependency nodes; the
   executor retrieves the required evidence under an eight-call budget; the
   verifier checks that every gold source was cited. Every seventh case injects
   a retrieval failure and records a bounded retry.
3. Inspect `reports/results.jsonl`. Compare `single_agent`,
   `planner_executor`, and `specialist_decomposition` on the same cases and
   budget. Then inspect `reports/metrics.json` for metrics derived from those
   raw rows.
4. Run `make check-step-1`, then `make check-step-2`; each check reads the
   generated reports and prints observed versus required evidence.

Expected pinned run: 24 cases, planner-executor budget compliance `1.0`, and
non-zero recovery cases. Latency may differ slightly across machines.
