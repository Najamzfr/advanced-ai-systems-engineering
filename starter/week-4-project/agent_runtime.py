"""Callable Week 4 planner–executor runtime.

This is the small integration surface used by later weekly builds.  It runs
the same planner, retriever, executor and verifier as ``project.py``; it does
not replay a saved trajectory.  The interface remains dependency-free so it
can be used in an offline starter archive.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

_PROJECT_PATH = Path(__file__).with_name("project.py")
_SPEC = importlib.util.spec_from_file_location("week4_runtime_project", _PROJECT_PATH)
if _SPEC is None or _SPEC.loader is None:  # pragma: no cover - impossible in a valid starter
    raise RuntimeError(f"cannot load {_PROJECT_PATH}")
_PROJECT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_PROJECT)
BUDGET, execute, retrieve = _PROJECT.BUDGET, _PROJECT.execute, _PROJECT.retrieve


def execute_request(question: str, request_id: str, failure_mode: str | None = None,
                    expected_evidence: list[str] | None = None,
                    metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute one live, bounded planner-executor request.

    ``expected_evidence`` is optional for operational callers.  In that case
    the verifier records that it performed a retrieval-grounded check rather
    than claiming benchmark-gold completeness.  ``failure_mode`` currently
    supports ``retrieval_timeout`` / ``tool_timeout`` as a retry injection.
    """
    corpus = [json.loads(line) for line in (_PROJECT_PATH.parent / "data" / "corpus.jsonl").read_text().splitlines() if line.strip()]
    observed = retrieve(question, corpus, k=4)
    has_benchmark_gold = expected_evidence is not None
    row = {
        "case_id": request_id,
        "question": question,
        "gold_evidence": list(expected_evidence or observed[:1]),
        "steps": [
            "find relevant documentation evidence",
            "cross-check the evidence before answering",
            "verify citations and bounded execution",
        ],
        "inject_failure": failure_mode in {"retrieval_timeout", "tool_timeout", "transient_failure"},
    }
    result = execute(row, corpus, "planner_executor")
    result["request_id"] = request_id
    result["runtime"] = {
        "name": "week4_planner_executor",
        "live_execution": True,
        "failure_mode": failure_mode or "none",
        "budget": BUDGET,
        "metadata": metadata or {},
    }
    result["verification"]["verification_scope"] = (
        "benchmark_gold" if has_benchmark_gold else "retrieval_grounded_operational"
    )
    result["verification"]["observed_candidates"] = observed
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the live Week 4 agent runtime")
    parser.add_argument("--question", required=True)
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--failure-mode")
    parser.add_argument("--expected-evidence", default="[]", help="JSON list of document IDs")
    args = parser.parse_args()
    try:
        expected = json.loads(args.expected_evidence)
        if not isinstance(expected, list):
            raise ValueError
    except ValueError as exc:
        raise SystemExit("--expected-evidence must be a JSON list") from exc
    print(json.dumps(execute_request(args.question, args.request_id, args.failure_mode, expected), indent=2))


if __name__ == "__main__":
    main()
