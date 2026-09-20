# Week 7 — Durable, observable agent operations

Build a workflow that can restart safely, pause for approval, retry a transient failure, compensate a failed side effect, and leave a dead-letter record when recovery is impossible. The same runner emits OpenTelemetry traces, metrics and logs through OTLP/HTTP.

## Quickstart

```bash
make setup
make run
make test
make grade
```

The smoke command runs the checked-in fixture. For the assignment dataset:

```bash
python scripts/fetch_data.py --cases 20
make evaluate
make grade
```

For the cumulative path, point the fetcher at the Week 4 project. The imported
request ID is retained as the Week 7 run ID. During evaluation, Week 7 calls
the live Week 4 `agent_runtime.py` for every request and emits planner,
executor, and verifier spans around that call; the saved Week 4 result remains
provenance for auditability:

```bash
python scripts/fetch_data.py --cases 20 --from-week4 ../week-4-project
python project.py --require-real-data --approve --from-week4 ../week-4-project
```

`reports/results.jsonl` contains one durable state result per run. `state/<run_id>.json` contains the event journal and idempotency ledger. `reports/telemetry.ndjson` is an audit copy even when no collector is running.

Imported runs contain `source.mode=imported_week4_planner_executor` and
planner, executor, and verifier spans tied to the same request ID. Their span
durations are measured by the Week 7 process; the Week 4 reported latency is
kept only as source evidence. The course-owned fixture remains an explicit
local fallback when no Week 4 artifact is supplied.

## Grafana stack

Start the local stack with `docker compose up -d`, then run `make evaluate` or `make telemetry`. Grafana is at `http://localhost:3000`; Prometheus is at `http://localhost:9090`. The runner posts to `http://localhost:4318/v1/{traces,metrics,logs}`. The dashboard uses the provisioned Tempo, Prometheus and Loki data sources.

The stack is optional for grading: the local telemetry audit is mandatory, while OTLP delivery is recorded as best-effort so learners can complete the build without Docker.

## Failure exercise

`tool_timeout` and `model_timeout` cases produce an error span followed by a retry span and a recovery log. Cases requiring approval pause in `WAITING_APPROVAL` unless `--approve` is supplied. Every write is keyed by `case_id + step`; replaying a state journal produces an idempotency hit rather than a second effect.

## Evidence standard

Do not edit `reports/metrics.json` by hand. The checker recomputes case, trace, journal, retry and telemetry evidence from raw results. A dashboard screenshot is supplementary; the machine-readable report is the source of truth.
