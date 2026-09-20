# Week 8 release defense

## Decision

CONDITIONAL — derived from live component results in `results.jsonl`.

## Evidence

- Cases: 3
- Runtime: smoke_fixture
- Components: week2_retrieval, week3_mcp, week4_planner_executor, week5_security, week6_adapter, week7_workflow
- Latency p95 (ms): 0.004
- Cost per successful task (USD): 0.000000
- Failure boundaries exercised: 5

## Limits

Smoke mode is intentionally non-promotable. A release is valid only when this runner invokes the Week 2 retrieval, Week 3 MCP boundary, Week 4 planner-executor, Week 5 policy boundary, Week 6 strict PEFT adapter, and Week 7 durable telemetry workflow from the supplied course-work directory. Provider-backed model quality remains a separate production experiment.
