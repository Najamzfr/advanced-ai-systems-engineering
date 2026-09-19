# Week 2 reference solution

A deterministic six-method ablation reference gives you concrete report shape, denominators and citation provenance.

Run `make setup`, then `make run`. Open `reports/metrics.json` and verify the smoke denominator before touching retrieval code. Run `make check-step-1`; it should identify the exact report keys needed before you fetch QASPER.

The smoke path is a wiring check. The real-data target is: Reference target: 200+ questions, six method rows, Recall@5/MRR@5 with denominators, and every citation linked to a document/page ID.
