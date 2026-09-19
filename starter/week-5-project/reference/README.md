# Week 5 reference solution

The reference red-team pack includes attack categories, benign controls, boundary policy evidence and a before/after comparison.

Run the smoke attack runner and label each case by effect. Confirm that benign controls are counted separately. Run `make check-step-1`; it should pass only when the harness can distinguish attack and benign rows.

The smoke path is a wiring check. The real-data target is: Reference target: 50+ attacks, benign success denominator, attack success before/after, and one mitigation covered by regression tests.
