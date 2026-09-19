# Week 3 reference solution

The reference runtime shows typed tool contracts, a two-read-plus-write trace and idempotent recovery evidence.

Run the smoke path and open the trajectory report. Trace one request from tool discovery to validation to execution. Run `make check-step-1` before adding a live API; the first pass is about contract boundaries, not network access.

The smoke path is a wiring check. The real-data target is: Reference target: 20+ trajectories, valid arguments, two read tools, one controlled write, and zero duplicate effects in the fixture.
