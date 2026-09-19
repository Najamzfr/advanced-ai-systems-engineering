# Week 7 reference solution

The reference observability pack includes trace fields, dashboard queries, cost formulas and a failure-injection narrative.

Start the local stack, run one smoke request and inspect its run ID across retrieval, model and tool spans. Run `make check-step-1` before provisioning the full dashboard.

The smoke path is a wiring check. The real-data target is: Reference target: 20 real runs, complete traces, latency p95, retries, tokens, cost and one trace-plus-log failure investigation.
