# Week 6 — Adapt a classifier and measure the serving trade-offs

This build uses the public [BANKING77](https://huggingface.co/datasets/PolyAI/banking77)
intent dataset. `make setup` downloads the pinned train/test files when network access is
available and records their SHA-256 checksums. In an offline classroom the checked-in
`data/sample.jsonl` is used as a clearly-labelled smoke fixture; it is never described as
the benchmark dataset.

The experiment keeps train and test records separate and compares six executable
conditions: prompt-only, lexical retrieval (RAG), an adapter trained on the training
split, and three explicit hybrid routes. The default adapter is a small hashed-feature
linear adapter that runs without a GPU. It is a smoke-test fallback, **not** a completed
LoRA build. The strict real-adapter route uses `torch`, `transformers`, `peft`, and the
tiny model named by `WEEK6_MODEL_NAME` (default:
`hf-internal-testing/tiny-random-distilbert`) on at most 64 local training rows. If model
loading or training fails, `make run-lora` fails rather than silently substituting the
fallback.

```bash
make setup
make run                 # smoke experiment, writes reports/metrics.json
make evaluate            # full local benchmark (or `--limit N`)
make install-lora        # install optional dependencies for a real LoRA run
make run-lora            # strict real PEFT/LoRA run; required for step 8
make run-qlora           # strict 4-bit QLoRA run; requires CUDA + bitsandbytes
make test                # contract and fallback/real-path tests
make check-step-1        # each of the 12 build checks is independent
make grade
```

Required evidence is `reports/metrics.json`, `reports/results.jsonl`,
`reports/leakage.json`, and `reports/adaptation_report.md`. Never report test accuracy
from training rows. A real GPU/LoRA run must include its model ID, hardware and package
versions in the report.

Install the real route with `make install-lora`, then run `make run-lora`. Set
`WEEK6_MODEL_NAME` to a cached/local compatible sequence-classification model if the
default tiny model is unavailable; set `WEEK6_PEFT_TRAIN_LIMIT` to change the small
training slice. The report records the model, rank, package versions, hardware, training
time, and execution mode. `make grade` intentionally fails at step 8 after an offline
fallback: only `transformers_peft_lora` or `transformers_peft_qlora` completes the build.
