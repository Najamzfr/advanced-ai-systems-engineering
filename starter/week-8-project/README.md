# Week 8 — production release starter

This is a small, dependency-free release harness for the Week 8 build. It joins the evaluation, security, recovery and observability contracts into one deployable HTTP service. The runtime records raw evidence first and derives the release report from those records; no metric is typed in as a score.

## Quick start

```bash
make setup
make run
make check-step-1
make test
```

`make run` executes the explicit three-record smoke fixture. It is not a
release and cannot pass promotion. A release pack must be built from all seven
upstream projects; `--upstream-root` is mandatory for the 150-case release:

```bash
python scripts/fetch_data.py --cases 150 --upstream-root ../course-work
COURSE_WORK_ROOT=../course-work make evaluate
make grade
```

The command materializes cases from the raw `reports/results.jsonl` files of
Weeks 1–7 and records their checksums in `data/upstream-evidence.json`.
`make evaluate` then executes every release request through the live Week 2
retrieval, Week 3 MCP, Week 4 planner-executor, Week 5 policy boundary, Week 6
adapter, and Week 7 durable workflow/telemetry runtimes. Promotion requires
strict PEFT LoRA/QLoRA evidence from Week 6; fallback adaptation remains useful
for practice but cannot pass release grading. It does not replay saved answers. The
generated `reports/` directory is intentionally ignored by the starter archive.

## Service and deployment

```bash
python serve.py
curl http://localhost:8080/healthz
curl http://localhost:8080/readyz
curl -X POST http://localhost:8080/v1/ask \
  -H 'content-type: application/json' \
  -d '{"question":"What is the release status?"}'
docker compose up --build
```

For Compose, export `COURSE_WORK_ROOT` to the host directory that contains the
seven previous projects. It is mounted at `/course-work`; `/v1/ask` therefore
uses the same live composition. Without that mount, only the explicit smoke
fixture is available and promotion must fail.

Configuration is read from environment variables. Copy `.env.example` to `.env`; never commit provider keys. `MODEL_API_KEY` is optional for this offline reference, but production adapters must use a secret manager.

## Failure matrix

The release runner injects one boundary failure per case: model unavailable, retrieval unavailable, tool timeout, database timeout and approval timeout. Each failure has a bounded policy (fallback, cached context, retry, or pending state), an observed outcome, latency and cost. A failure is not counted as success merely because the process stayed alive.

## Evidence

`reports/release_report.json` is machine-readable and includes raw case count, quality, SLOs, cost, recovery and failure rows. `reports/final_report.md` is the human defense. `make grade` recomputes checks from these files and fails on fabricated or incomplete evidence.
