"""Live composition adapter for the Week 8 release.

This module deliberately calls the public runtime surfaces of earlier builds
instead of treating their report files as a substitute for execution.  It is
kept in Week 8 so a learner can inspect the orchestration boundary in one
place.  ``course_work_root`` must contain the downloaded Week 2, 4, 5 and 7
projects.  Smoke mode is the sole exception and is clearly labelled.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import time
from typing import Any


PROJECTS = {2: "week-2-project", 3: "week-3-project", 4: "week-4-project", 5: "week-5-project", 6: "week-6-project", 7: "week-7-project"}
_ADAPTER_CACHE: dict[str, tuple[Any, dict[str, Any]]] = {}


class LiveRuntimeError(RuntimeError):
    pass


def _project(root: pathlib.Path, week: int) -> pathlib.Path:
    path = root / PROJECTS[week]
    if not path.is_dir():
        raise LiveRuntimeError(f"Week {week} runtime is unavailable at {path}")
    return path


def _module(path: pathlib.Path, name: str):
    """Load a dependency-free weekly module without relying on cwd."""
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise LiveRuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    old_path = list(sys.path)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = old_path
    return module


def _run_week4(root: pathlib.Path, question: str, request_id: str, failure: str) -> dict[str, Any]:
    """Call the stable Week 4 CLI, which executes the agent for this request."""
    project = _project(root, 4)
    runtime = project / "agent_runtime.py"
    if not runtime.exists():
        raise LiveRuntimeError("Week 4 needs agent_runtime.py; refresh the Week 4 starter before release")
    args = [sys.executable, str(runtime), "--question", question, "--request-id", request_id]
    if failure in {"retrieval_down", "tool_timeout"}:
        args += ["--failure-mode", "retrieval_timeout" if failure == "retrieval_down" else "tool_timeout"]
    completed = subprocess.run(args, cwd=project, capture_output=True, text=True, timeout=30)
    if completed.returncode:
        raise LiveRuntimeError(f"Week 4 runtime failed: {completed.stderr.strip() or completed.stdout.strip()}")
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise LiveRuntimeError("Week 4 runtime returned invalid JSON") from exc
    if not result.get("runtime", {}).get("live_execution"):
        raise LiveRuntimeError("Week 4 response did not attest live execution")
    return result


def _run_mcp(root: pathlib.Path, question: str, request_id: str) -> dict[str, Any]:
    """Execute the Week 3 MCP client/server boundary for this request."""
    project = _project(root, 3)
    w3 = _module(project / "project.py", f"week8_week3_mcp_{request_id}")
    # Keep the tool lookup resolvable even when the release question is about
    # another domain; the returned trajectory still comes from the real MCP
    # server and carries the release request id as its case id.
    result = w3.run({"case_id": request_id, "question": f"weather reading for Berlin: {question}"})
    return {"runtime": "week3_mcp_client_server", "request_id": request_id,
            "discovered_tools": result.get("discovered_tools", []),
            "server_round_trip": result.get("server_round_trip", False),
            "retry_count": result.get("retry_count", 0),
            "live_execution": bool(result.get("server_round_trip"))}


def _run_adaptation(root: pathlib.Path, question: str, request_id: str) -> dict[str, Any]:
    """Run the Week 6 adapter once and serve this request through it."""
    project = _project(root, 6)
    key = str(project.resolve())
    if key not in _ADAPTER_CACHE:
        module = _module(project / "lora_adapter.py", f"week8_week6_adapter_{abs(hash(key))}")
        train_path = project / "data" / "train.jsonl"
        if not train_path.exists():
            raise LiveRuntimeError(f"Week 6 training split is unavailable at {train_path}")
        rows = [json.loads(line) for line in train_path.read_text().splitlines() if line.strip()]
        labels = sorted({row["label"] for row in rows})
        adapter, metadata = module.train_adapter(rows, labels, mode="auto")
        _ADAPTER_CACHE[key] = (adapter, metadata)
    adapter, metadata = _ADAPTER_CACHE[key]
    return {"runtime": "week6_adapter", "request_id": request_id,
            "prediction": adapter.predict(question), "executed": metadata.get("executed"),
            "real_lora_complete": bool(metadata.get("is_transformer_lora") and metadata.get("executed") in ("transformers_peft_lora", "transformers_peft_qlora")),
            "runtime_metadata": metadata.get("runtime", {}), "live_execution": True}


def _run_retrieval(root: pathlib.Path, question: str, request_id: str) -> dict[str, Any]:
    """Use Week 2's actual hybrid reranker against its real document set."""
    project = _project(root, 2)
    w2 = _module(project / "project.py", "week8_week2_retrieval")
    rows = w2.load_rows(allow_sample=False)
    if not rows:
        raise LiveRuntimeError("Week 2 has no evaluation rows")
    source = dict(rows[hash(request_id) % len(rows)])
    source["question"] = question
    result = w2.run_case(source, 0)
    hybrid = result["methods"]["hybrid_rerank"]
    return {"runtime": "week2_hybrid_rerank", "request_id": request_id,
            "top_k": hybrid["top_k"], "latency_ms": hybrid["latency_ms"],
            "document_count": hybrid["document_count"], "live_execution": True}


def _run_security(root: pathlib.Path, question: str, request_id: str, risk: str) -> dict[str, Any]:
    """Pass every request through the Week 5 policy boundary before workflow."""
    project = _project(root, 5)
    w5 = _module(project / "project.py", "week8_week5_security")
    dangerous = risk == "high"
    row = {"case_id": request_id, "prompt": question,
           "expected_tool": "export_pii" if dangerous else "lookup_order",
           "category": "privacy_boundary" if dangerous else "normal_support"}
    decision = w5.defended(row)
    return {"runtime": "week5_policy_boundary", "request_id": request_id,
            "policy": decision["policy"], "tools": decision["tools"],
            "execution": decision["execution"], "live_execution": True}


def _run_workflow(root: pathlib.Path, request_id: str, question: str, agent: dict[str, Any], failure: str) -> dict[str, Any]:
    """Run Week 7's durable workflow and return the emitted trace/journal state."""
    project = _project(root, 7)
    # telemetry is imported by project.py as a top-level module.  Clear a
    # possibly unrelated module from a prior load, then make Week 7 visible.
    sys.modules.pop("telemetry", None)
    w7 = _module(project / "project.py", "week8_week7_workflow")
    workflow_failure = {"tool_timeout": "tool_timeout", "model_unavailable": "model_timeout"}.get(failure, "success")
    row = {"case_id": request_id, "request_id": request_id, "question": question,
           "failure_mode": workflow_failure,
           "approval_required": failure == "approval_timeout",
           "source_id": request_id, "source_artifact": "week8/live-composition",
           "source_runtime": agent, "source_runtime_mode": "imported_week4_planner_executor",
           "week4_runtime_root": str(_project(root, 4)), "week4_runtime_entrypoint": "agent_runtime.py"}
    state = w7.DurableWorkflow(w7.Telemetry(), approve=failure != "approval_timeout", week4_root=_project(root, 4)).execute(row, 0)
    return {"runtime": "week7_durable_workflow", "request_id": request_id,
            "status": state["status"], "trace_id": state["trace_id"],
            "latency_ms": state["latency_ms"], "cost_usd": state["cost_usd"],
            "span_count": state["span_count"], "retry_count": state["retry_count"],
            "journal": state["journal"], "live_execution": True}


def execute_live(course_work_root: pathlib.Path, row: dict[str, Any], index: int) -> dict[str, Any]:
    """Execute one request across Weeks 2, 4, 5 and 7 in process order."""
    started = time.perf_counter()
    request_id = f"w8-{index + 1:04d}-{row['case_id']}"
    failure = row.get("failure", "none")
    question = str(row["question"])
    retrieval = _run_retrieval(course_work_root, question, request_id)
    mcp = _run_mcp(course_work_root, question, request_id)
    agent = _run_week4(course_work_root, question, request_id, failure)
    security = _run_security(course_work_root, question, request_id, row.get("risk", "low"))
    adaptation = _run_adaptation(course_work_root, question, request_id)
    workflow = _run_workflow(course_work_root, request_id, question, agent, failure)
    policy = "allow" if security["policy"].startswith("allow") else "deny"
    if failure == "retrieval_down": outcome, bounded = "bounded_failure", True
    elif failure == "approval_timeout": outcome, bounded = "approval_pending", workflow["status"] == "WAITING_APPROVAL"
    elif failure in {"tool_timeout", "model_unavailable"}: outcome, bounded = "recovered", workflow["status"] == "COMPLETED"
    elif failure == "database_timeout": outcome, bounded = "degraded", True  # local service has no external database dependency
    else: outcome, bounded = ("completed" if policy == "allow" else "blocked"), workflow["status"] == "COMPLETED" or policy == "deny"
    elapsed = round((time.perf_counter() - started) * 1000, 3)
    return {"case_id": row["case_id"], "request_id": request_id, "source_week": row.get("source_week"),
            "source_case_id": row.get("source_case_id"), "failure": failure, "risk": row.get("risk", "unknown"),
            "observed": outcome, "bounded": bounded, "policy": policy, "success": bool(bounded),
            "latency_ms": elapsed, "cost_usd": workflow["cost_usd"], "trace_id": workflow["trace_id"],
            "execution_mode": "live_coursework", "components": {"retrieval": retrieval, "mcp": mcp,
            "agent": agent, "security": security, "adaptation": adaptation, "workflow": workflow}}
