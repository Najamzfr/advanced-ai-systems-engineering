# Week 7 observability report

- **trace completeness:** 1.0
- **latency p50/p95:** [8.508, 20.446]
- **error rate:** 0.0
- **retry rate:** 0.3333
- **tokens/request:** 90
- **cost/request:** 0.00045

## Durable execution evidence

Every case has a JSON journal and idempotency action IDs under `state/`. Approval cases remain `WAITING_APPROVAL` unless `--approve` is supplied; retries are visible as error and retry spans. The local NDJSON copy is the audit fallback when the collector is unavailable.

## Imported Week 4 runtime

When fetched with `--from-week4`, each run retains the Week 4 request ID, source artifact, planner-executor result, and planner/executor/verifier spans. Span durations are measured wall-clock durations from this run; the source latency is recorded as an attribute, not substituted for observed timing.

## Failure injection

The tool and model timeout fixtures emit an error span, retry event, and recovery log. Inspect the same `trace_id` in `reports/results.jsonl` and Grafana/Loki when Docker Compose is running.
