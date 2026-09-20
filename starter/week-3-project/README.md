# Week 3 — Production bounded tool-using agent

This starter is an executable, offline-first reference for building a bounded
agent that calls typed tools through an MCP-compatible JSON-RPC client. The
runner starts `mcp_server.py` as a subprocess, discovers tools, validates
arguments, retries one transient failure, and writes through an idempotency key.
No trajectory is fabricated: `reports/results.jsonl` is emitted from the
actual server responses.

```text
make setup
make run                 # three local smoke cases
python scripts/fetch_data.py --cases 20
make evaluate            # public Open-Meteo slice
make test
make grade
```

Verify the retry and idempotency boundary with one explicit, deterministic
failure (it is never injected silently):

```text
python project.py --allow-sample --inject-one-failure
```

The public slice uses Open-Meteo current-weather responses for 20 distinct
coordinates. Network failure is explicit; the fetcher never pads a dataset by
repeating a response. The smoke fixture is intentionally not grade evidence.

Required report: `reports/agent_decision.md`. Required metrics are computed
from raw tool call evidence: tool-selection accuracy, argument validity,
successful completion rate, retry rate, and duplicate-effect rate.
