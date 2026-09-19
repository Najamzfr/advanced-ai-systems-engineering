# Week 6 reference solution

The reference study shows leakage checks, six baseline rows and a capacity recommendation tied to measured serving behavior.

Run the smoke experiment and inspect the split manifest. Verify that train, development and test IDs are distinct before reading quality metrics. Run `make check-step-1` as the exit condition.

The smoke path is a wiring check. The real-data target is: Reference target: 300+ labeled cases, leakage-free splits, six comparisons, and quality/latency/memory evidence.
