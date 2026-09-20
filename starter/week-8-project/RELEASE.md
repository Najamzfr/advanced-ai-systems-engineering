# Release contract

The release is promotable only when `make grade` passes. Promotion requires a materialized manifest, at least 150 unique cases, all five injected failure boundaries, complete trace fields, latency and cost SLOs, and a final report that names limitations.

`integration/upstream-contract.json` and `integration/deployment-contract.json`
record the seven upstream domains and the HTTP/monitoring contract. A release
must be materialized with `python scripts/fetch_data.py --cases 150
--upstream-root ../course-work`; the script requires raw result rows plus the
domain-specific evidence files, replays those rows, and records commit-free
content checksums in `data/upstream-evidence.json`.

The container exposes `/healthz` for process health and `/readyz` for dataset/runtime readiness. `/v1/ask` returns a trace ID and observed policy so an operator can connect an answer to release evidence.
