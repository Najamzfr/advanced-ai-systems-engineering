# Week 5 — Red-team and harden an agent

This project evaluates a bounded customer-operations agent against a fixed, versioned attack pack and benign controls. It is deliberately offline: no provider key is required and no real side effect is ever executed. The harness models the complete decision path—intent, retrieval, planning, tool authorization, execution, answer and policy—so a learner can see where a defense succeeds or fails.

## Quickstart

```bash
make setup
make run
make grade
```

`make run` evaluates the checked-in smoke fixture. For the assignment-sized pack:

```bash
python scripts/fetch_data.py --cases 50
make evaluate
make grade
```

To red-team the planner-executor built in Week 4, import its measured raw
trajectory artifact. The 50-case pack is retained, and every case records the
Week 4 case id, artifact hash, planner budget, verification decision, and the
Week 5 boundary decision. Evaluation then calls Week 4's live
`agent_runtime.py` for every attack and control prompt in a no-side-effect
sandbox; the saved trajectory is provenance, not a substitute for execution:

```bash
python scripts/fetch_data.py --cases 50 --from-week4 ../week-4-project
python project.py --require-real-data --from-week4 ../week-4-project
make grade
```

An imported trajectory is accepted only when its verifier succeeded within its
declared call budget. Otherwise it is quarantined before tool authorization.
`data/eval.jsonl` and `reports/results.jsonl` preserve the provenance needed to
replay that decision; the runner never replaces the imported agent with a
standalone hard-coded trajectory.

Inspect `reports/results.jsonl` before reading the aggregate. Every row contains the expected action, every layer's decision, and the before/after outcome. `reports/red_team_report.json` is generated from those rows; it is not a hand-written score.

The pack is course-owned and intentionally contains no customer data. Its manifest records the version, case counts, categories, SHA-256 and license. Replace it only with a reviewed pack that preserves the same schema and benign controls.

## What is measured

- attack success rate before and after the defense;
- unauthorized tool-call rate;
- benign task success and false-refusal rate;
- recovery rate for approved retries;
- per-layer disagreement (intent, retrieval, planning, tools, execution, answer, policy);
- attack-category confusion and regression cases.

The `before` policy is a deliberately unsafe baseline. The `after` policy uses deny-by-default tool authorization, explicit approval for irreversible actions, prompt-injection isolation, and an answer gate that refuses unsupported completion claims.

## Reproduce individual checkpoints

Run `make check-step-1` through `make check-step-12`. Each check reads the manifest, raw rows or generated report and reports the observed value and required value. The checker never trusts a learner-supplied `step_evidence` flag.
