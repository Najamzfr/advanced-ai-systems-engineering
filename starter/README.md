# A/SE engineering fixtures

Prerequisites: Python 3.10 or newer. No package installation, API key, GPU, or external service is required for these fixtures.

    python coursekit.py all

Expected: retrieval recall and reciprocal rank 0.5; contract outcomes OK, DENIED_SCOPE, SCHEMA_ERROR; 512 MiB KV/sequence; one logical dispatch and delivered outbox state. JSON is saved in results/all.json.

These are worked engineering examples, not complete labs or measured model runs. The course supplies full requirements and the guided transition to your own implementation. Do not report fixture outputs as live model quality, distributed exactly-once guarantees, or GPU benchmarks.

- Week 1: adapt the JSON result shape into a provider/evaluator harness; introduce real cases and separate replay/live modes.
- Week 2: replace ranked/relevant IDs with actual retrieved and human-labeled evidence; add Recall@5/10, MRR, NDCG aggregation and six retrieval conditions. Empty relevance uses null, not a made-up perfect score.
- Week 3: turn contract validation into scoped tools; implement MCP using the curriculum-pinned specification and a pinned SDK. The fixture is not an MCP implementation.
- Week 4: add typed plan tasks, dependencies, acceptance criteria and equal-budget architecture runs.
- Week 5: extend contracts with 50 threat cases, benign controls, exact action approval and explicit denial audit.
- Week 6: replace the illustrative KV configuration with your chosen model's actual values; run and label real adaptation/serving experiments separately.
- Week 7: replace the in-memory demonstration with a persistent database, separate sandbox sink, worker process and crash injection. The local fixture illustrates reconciliation; it does not prove distributed recovery.
- Week 8: combine the evidence into the 150-scenario project evaluation and a reproducible release.

Never use real contacts or external dispatch for course campaign actions. Use synthetic consent/contact fixtures and the sandbox sink.
