# Week 4 reference solution

The reference release compares single-agent and planner-executor behavior under equal budgets with explicit evidence completeness.

Run the smoke project and inspect the task graph before inspecting model output. Verify that every subtask has an acceptance condition, then run `make check-step-1`. Only then add the held-out multi-hop set.

The smoke path is a wiring check. The real-data target is: Reference target: 25 held-out multi-part questions, equal budgets, task success plus evidence completeness, and a documented complexity decision.
