# Week 5 red-team report

Cases: 4 (attacks: 2, benign controls: 2)

## Measured metrics

- **attack success rate before**: 1.0
- **attack success rate after**: 0.0
- **attack prevention rate**: 1.0
- **benign task success**: 0.0
- **unauthorized tool-call rate**: 0.0
- **false refusal rate**: 1.0
- **recovery rate**: 1.0

## Boundary

The baseline is intentionally unsafe. The defended path denies untrusted or irreversible tool requests and keeps benign controls read-only. This offline fixture does not execute external side effects; provider and deployment runs must preserve the raw evidence contract.
