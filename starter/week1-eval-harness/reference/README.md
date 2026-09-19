# Week 1 reference solution

This reference is intentionally small and deterministic. It demonstrates the
shape of a defensible evaluation run without pretending that the three-case
fixture is a benchmark. Compare your file layout, metric denominators and
decision narrative against it; do not copy its provider logic as a quality
claim.

## Reproduce the reference smoke output

```text
make setup
make run
make check-step-1
```

Expected: two model keys, three cases per model, schema validity `1.0`, and a
judge denominator of `0`. The real submission must replace the fixture with
300+ frozen BANKING77 cases, at least 15 cases for every intent in the fixed
confusion-prone slice, plus 30 adjudicated rows.
