# Week 2 — Measured retrieval system

This starter evaluates six retrieval configurations against the same QASPER document snapshot: BM25, hashed dense embeddings, reciprocal-rank hybrid fusion, a query-aware reranker, document-level navigation without a vector index, and a long-context baseline. It records raw rankings in `reports/results.jsonl`, computes Recall@5/MRR@5/citation precision separately from an oracle-context answer check, and preserves question/evidence/document provenance.

```bash
make setup
python scripts/fetch_data.py --cases 200
make evaluate
make grade
make check-step-6
```

Query the downloaded corpus with an explicitly extractive, cited answer:

```bash
python project.py --require-real-data --ask "What evidence supports the reported result?"
```

`make run` is only a three-row smoke fixture. It must not be used as the final report. The public downloader fails loudly if QASPER cannot be fetched, excludes questions without resolvable source evidence, and never pads or repeats rows. `answer correctness` is an oracle-context control and is not a claim about generative answer quality. The Q&A command returns source excerpts and citations rather than pretending an extractive baseline is a generative assistant.
