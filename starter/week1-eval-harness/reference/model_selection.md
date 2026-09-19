# Reference model-selection memo

This memo demonstrates the required structure. Its three-case smoke numbers
prove only that the harness runs; they are not a deployable benchmark.

## Decision

No model is selected from the smoke fixture. `baseline-v1` and `robust-v2`
both classify the three worked examples correctly, but the sample excludes
most BANKING77 intents and contains no hard confusion pairs. The decision is
therefore “collect the required evidence,” not “ship either model.” The
fallback configuration remains `baseline-v1` only for local wiring tests.

## Evidence

| Measure | baseline-v1 | robust-v2 | Denominator / source |
| --- | ---: | ---: | --- |
| Macro F1 | 1.000 | 1.000 | 3 smoke cases per model |
| Schema validity | 1.000 | 1.000 | 3 outputs per model |
| Latency p95 (ms) | 0.060 | 0.008 | 3 local calls per model |
| Cost per successful case | 0.000 | 0.000 | deterministic local adapters |
| Judge agreement | 0.000 | 0.000 | 0 audited rows; invalid for selection |

The equal macro F1 is expected because the fixture contains one obvious case
for each of three labels. Schema validity confirms that both adapters respect
the output contract. The latency values are local timing observations and are
too small and unstable to compare as provider performance. Cost is zero only
because these are deterministic teaching adapters, not paid provider calls.

## Failure analysis

The smoke run contains no observed classification failures, which is itself a
coverage failure. It does not test `card_arrival` against
`card_delivery_estimate`, pending against declined cash withdrawal, recognised
against unrecognised card payments, or failed against reverted top-ups. The
real run must preserve those cases and list representative wrong predictions
with expected label, predicted label and a plausible mechanism.

## Judge calibration

Judge agreement is not available because the denominator is 0 rather than the
required 30 human-reviewed rows. Before model selection, adjudicate a fixed
sample, report disagreement categories and preserve at least one example where
the judge and reviewer diverge. Agreement without the denominator is not
evidence.

## Deployment recommendation

Do not deploy from this result. Run both configurations on the same 300-case
split, populate all five metric rows and compare the fixed confusion set. If a
selected model violates the schema contract or exceeds the declared latency or
cost boundary, route to the documented fallback. Escalate low-confidence or
high-risk intents rather than hiding them inside aggregate accuracy.

## Limitations

This reference establishes file shape, metric names and decision discipline.
It does not establish production quality, provider reliability, realistic
cost, tail latency or calibrated judge behavior. A valid memo must replace the
smoke values with reproducible real-run evidence and state what result would
reverse its recommendation.
