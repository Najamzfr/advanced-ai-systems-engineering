# Advanced AI Systems Engineering
## 8-Week Graduate-Level AI Engineering Course — ChatGPT Work Handoff

> **Purpose of this document**  
> This file is the complete project brief, curriculum specification, design intent, reference map, and conversation handoff for building an advanced AI engineering course website in ChatGPT Work.

---

# 1. Project Idea

Build a rigorous, advanced-level AI engineering course that takes a learner who already understands the foundations of LLM engineering and develops them toward the technical breadth, architecture judgment, evaluation discipline, and production engineering capability expected from a strong senior AI engineer.

The course should **not** be another beginner RAG / agent tutorial collection.

It should be structured more like a graduate-level MIT / Stanford / Berkeley engineering course:

- theory
- primary readings
- research papers
- systems concepts
- implementation from first principles
- labs
- quizzes
- assignments
- architecture decision records
- evaluations
- failure analysis
- design reviews
- two guided end-to-end real-world projects
- final technical defense

The central principle is:

> **Frameworks are tools, not the curriculum.**

The course should be organized around engineering problems:

- evaluation
- retrieval
- context
- state
- memory
- tool use
- planning
- multi-agent coordination
- security
- reliability
- observability
- workflow orchestration
- inference
- model adaptation
- system economics
- deployment
- production feedback loops

---

# 2. Main Goal

The goal is to create an **8-week, 100% free, advanced AI engineering program** for someone who already has LLM Zoomcamp-level foundations.

The intended learner should finish the course able to:

1. Design an AI system from an ambiguous business problem.
2. Decide when to use:
   - prompting
   - RAG
   - long context
   - tools
   - deterministic workflows
   - agents
   - multi-agent systems
   - fine-tuning
3. Build advanced retrieval systems beyond naive vector search.
4. Implement an agent loop from first principles.
5. Build production-ready tool-using agents.
6. Design and consume MCP servers.
7. Build durable workflows with approval gates and retries.
8. Evaluate models, retrieval, tools, plans, agent trajectories, and end responses separately.
9. Build reliable LLM-as-a-judge systems.
10. Perform adversarial testing and red-team agent systems.
11. Instrument AI systems with traces, metrics, logs, latency, and token usage.
12. Make cost / latency / quality trade-offs.
13. Understand LoRA, QLoRA, quantization, batching, KV cache, and serving trade-offs.
14. Design AI systems using queues, gateways, model routing, caching, and fallbacks.
15. Defend architecture decisions with experiments and evidence.
16. Produce professional engineering artifacts:
    - RFCs
    - ADRs
    - benchmark reports
    - evaluation suites
    - architecture diagrams
    - technical reports
    - reproducible repositories

---

# 3. Target Learner

The intended learner already has:

- Python
- APIs
- Git / GitHub
- Docker basics
- embeddings
- basic RAG
- vector databases
- prompt engineering
- LLM APIs
- simple evaluation
- LLM Zoomcamp or equivalent experience

This course should **not repeat basic LLM concepts** unless required for deeper understanding.

---

# 4. Expected Course Level

The desired rigor should feel closer to:

- MIT systems / ML engineering coursework
- Stanford AI systems coursework
- Berkeley graduate seminars
- serious production engineering bootcamps

The course should require approximately:

- **8 weeks**
- **18–25 hours per week**
- approximately **150–190 hours total**

This does **not** claim that eight weeks replaces years of professional experience.

The intended outcome is:

> A learner should reach the technical breadth and system-design maturity needed to perform strongly in senior-level AI engineering project work and interviews, while still needing real production experience to become truly senior in title and judgment.

---

# 5. Design Philosophy

The course should follow this loop every week:

```text
Theory
  ↓
Reading / Research Paper
  ↓
Implementation From Scratch
  ↓
Production Abstraction
  ↓
Experiment
  ↓
Evaluation
  ↓
Failure Analysis
  ↓
Engineering Artifact
```

The course should follow these rules:

## Rule 1 — Build before abstracting

Example:

Do not start agents with LangGraph.

First implement:

```python
while not finished:
    observation = environment.observe()
    decision = model(state, observation, tools)
    action = validate(decision)
    result = execute(action)
    state.update(result)
```

Then recreate the same system using a framework.

---

## Rule 2 — Evaluation before complexity

Before adding:

- more agents
- more tools
- more retrieval layers
- fine-tuning
- orchestration

there must already be a benchmark and evaluation methodology.

---

## Rule 3 — Architecture must be justified

Students should not be allowed to say:

- "I used RAG because RAG is best."
- "I used multi-agent because agents are powerful."
- "I fine-tuned because it improved the model."
- "I used LangGraph because it is production-ready."

They must show experiments.

---

## Rule 4 — Multi-agent is not automatically better

Students must compare:

1. single agent
2. planner/executor
3. multi-agent system

and measure:

- quality
- reliability
- latency
- token usage
- engineering complexity
- failure modes

---

## Rule 5 — Deterministic computation stays deterministic

LLMs should not replace:

- numerical calculations
- validation logic
- database constraints
- risk limits
- deterministic transformations
- authorization
- security controls

---

## Rule 6 — Every week produces an artifact

Examples:

```text
01-model-evaluation/
02-retrieval-ablation/
03-agent-runtime-mcp/
04-compound-ai-study/
05-agent-reliability/
06-adaptation-inference/
07-production-platform/
08-capstone-defense/
```

---

# 6. Reference Courses

The course is inspired by the following sources.

## Reference 1 — Alexey Grigorev
### AI Engineering Buildcamp: From RAG to Agents

https://maven.com/alexey-grigorev/from-rag-to-agents

Key ideas to borrow:

- RAG → Agents progression
- agent testing
- agent evaluation
- MCP
- production monitoring
- guardrails
- OpenTelemetry
- PydanticAI
- applied agents
- capstone-driven structure

Do **not** copy the course directly.

Use its scope as one major reference.

---

## Reference 2 — AI Engineering from Scratch

https://aiengineeringfromscratch.com/

This is also the main **website design inspiration**.

Key ideas:

- clean technical course layout
- academic / engineering aesthetic
- curriculum-first landing page
- modular lessons
- progress tracking
- artifact-oriented learning
- "understand before importing framework abstractions"
- individual pages for assignments / labs / lessons

The final website should feel similar in spirit:

- minimal
- technical
- curriculum-focused
- modern
- interactive
- clean typography
- module navigation
- visible progress

Do **not** copy branding, wording, code, or exact visual design.

---

## Reference 3 — UC Berkeley
### Large Language Model Agents, Fall 2024

https://rdi.berkeley.edu/llm-agents/f24

Important structural ideas:

- weekly research papers
- quizzes
- labs
- project milestones
- presentations
- reports
- research-level agent topics
- reasoning
- planning
- multi-agent systems
- software agents
- enterprise agents
- evaluation
- safety
- human-agent interaction

---

# 7. Main Book Reference

## Chip Huyen — AI Engineering

Official companion repository:

https://github.com/chiphuyen/aie-book

Table of contents:

https://github.com/chiphuyen/aie-book/blob/main/ToC.md

The course should assign selected sections rather than the entire book.

Core areas to use:

- Chapter 2 — model behavior / sampling / structured outputs
- Chapters 3–4 — evaluation
- Chapter 5 — prompting and context
- Chapter 6 — RAG and agents
- Chapter 7 — fine-tuning
- Chapter 8 — dataset engineering
- Chapter 9 — inference engineering
- Chapter 10 — production architecture / guardrails / orchestration / observability / feedback

---

# 8. Additional Primary Resources

Use free, high-quality sources wherever possible.

## Anthropic — Building Effective Agents

https://www.anthropic.com/engineering/building-effective-agents

Use for:

- workflow vs agent distinction
- routing
- parallelization
- orchestrator-worker
- evaluator-optimizer
- complexity trade-offs

---

## Anthropic — Context Engineering

https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

Use for:

- context design
- memory
- context compression
- information management
- agent context

---

## MCP Specification

https://modelcontextprotocol.io/specification/2025-06-18

Use for:

- MCP architecture
- clients
- servers
- tools
- resources
- prompts
- transports
- authorization

---

## MCP Python SDK

https://github.com/modelcontextprotocol/python-sdk

---

## OpenAI Agents SDK

https://github.com/openai/openai-agents-python

Documentation:

https://openai.github.io/openai-agents-python/

Use selectively for:

- agent patterns
- handoffs
- tools
- guardrails
- tracing
- human-in-the-loop

The course should remain provider-neutral.

---

## PydanticAI

https://github.com/pydantic/pydantic-ai

Documentation:

https://ai.pydantic.dev/

Use as the primary lightweight typed-agent framework after implementing primitives from scratch.

---

## Full Stack Deep Learning

https://fullstackdeeplearning.com/llm-bootcamp/

Useful for:

- LLMOps
- evaluation
- deployment
- testing
- monitoring
- production workflows

---

## OpenTelemetry

https://opentelemetry.io/docs/

Use for:

- traces
- spans
- logs
- metrics
- distributed tracing
- GenAI observability

---

## Grafana

https://grafana.com/docs/

---

## Evidently

https://docs.evidentlyai.com/

Use for:

- LLM evaluation
- monitoring
- regression tracking

---

## OWASP GenAI Security

https://genai.owasp.org/llm-top-10/

Use for:

- prompt injection
- excessive agency
- data leakage
- insecure output handling
- retrieval poisoning
- agent/tool security

---

## vLLM

https://docs.vllm.ai/

Use for:

- inference serving
- continuous batching
- KV caching
- PagedAttention
- prefix caching
- quantization
- speculative decoding

---

## n8n

Self-hosted AI starter kit:

https://github.com/n8n-io/self-hosted-ai-starter-kit

Use for:

- local workflow automation
- event-driven flows
- human approval
- scheduled pipelines
- integrating agents with deterministic workflows

---

# 9. Assessment Structure

| Component | Weight |
|---|---:|
| Weekly quizzes | 8% |
| Systems labs | 20% |
| Engineering assignments / ADRs | 16% |
| Reading / research summaries | 8% |
| Project 1 | 18% |
| Project 2 | 25% |
| Final technical defense | 5% |

---

# 10. Hard Pass Requirements

A learner cannot pass the course if:

- no automated evaluation exists
- projects cannot be reproduced
- agent tools are unrestricted
- the system has no tests
- no observability exists
- architecture decisions have no evidence
- projects cannot handle failures
- security testing is missing
- the final system cannot explain limitations

---

# 11. 8-Week Curriculum Overview

| Week | Core Theme | Major Output |
|---|---|---|
| 1 | Foundation Models & Evaluation Science | Model evaluation framework |
| 2 | Advanced Retrieval & Context Engineering | Retrieval ablation system |
| 3 | Agents From First Principles + MCP | Agent runtime + MCP |
| 4 | Planning, Compound AI & Multi-Agent | Project 1 |
| 5 | Reliability, Security & Agent Evaluation | Red-team/reliability suite |
| 6 | Fine-Tuning, Dataset & Inference Engineering | Adaptation/inference experiments |
| 7 | Production Architecture, Durable Workflows & Observability | Production platform |
| 8 | Senior AI System Design & Production Defense | Project 2 + technical defense |

---

# WEEK 1
# Foundation Models & Evaluation Science

## Goals

Understand models as engineering components rather than black-box chatbots.

Build a rigorous evaluation system before building advanced applications.

---

## Lecture Topics

### Foundation model behavior

- autoregressive generation
- logits
- token probability
- temperature
- top-p
- decoding
- structured outputs
- constrained generation
- test-time compute
- reasoning reliability
- uncertainty
- hallucination
- context-window behavior
- positional sensitivity
- capability boundaries
- model selection

---

## Evaluation Science

- evaluation-driven development
- exact evaluation
- semantic evaluation
- functional correctness
- task-specific metrics
- pairwise evaluation
- LLM-as-a-judge
- judge bias
- position bias
- verbosity bias
- judge calibration
- human evaluation
- regression testing
- adversarial cases
- confidence intervals
- cost
- latency

---

## Reading

### AI Engineering

Chapter 2:

- Sampling Fundamentals
- Sampling Strategies
- Test-Time Compute
- Structured Outputs
- Probabilistic Nature of AI

Chapter 3:

- Exact Evaluation
- Functional Correctness
- AI as a Judge
- Limitations of AI Judges
- Comparative Evaluation

Chapter 4:

- Evaluation Criteria
- Model Selection
- Cost and Latency
- Designing Evaluation Pipelines

---

## Lab 1
### LLM Behavioral Test Bench

Build:

```text
model-bench/
├── datasets/
├── evaluators/
├── providers/
├── experiments/
├── reports/
└── tests/
```

Compare at least two models.

Measure:

- factual correctness
- instruction following
- structured-output validity
- reasoning consistency
- long-context degradation
- latency
- token usage
- judge score

---

## Assignment 1
### Model Selection RFC

Scenario:

A customer-facing knowledge agent will process approximately:

**500,000 queries / month**

Design a model strategy.

Compare at least three options.

Discuss:

- primary model
- fallback
- routing
- latency
- quality
- monthly cost
- privacy
- failure behavior

Deliver:

- RFC ≤ 1,500 words
- benchmark
- architecture diagram
- decision table

---

## Quiz 1

1. Why is temperature not equivalent to uncertainty?
2. Why can average accuracy hide important production failures?
3. When is pairwise evaluation preferable?
4. What biases affect LLM judges?
5. Why must latency and cost be evaluated alongside model quality?
6. How would you detect a provider silently degrading model quality?

---

## Week 1 Artifact

```text
01-model-evaluation/
```

---

# WEEK 2
# Advanced Retrieval & Context Engineering

## Goals

Move beyond naive:

```text
chunk → embed → vector search → answer
```

Build retrieval systems scientifically.

---

## Topics

### Retrieval

- BM25
- inverted indexes
- embedding geometry
- ANN
- HNSW
- vector retrieval
- lexical retrieval
- hybrid retrieval
- reciprocal rank fusion
- reranking
- cross encoders
- metadata filters
- query expansion
- multi-query retrieval
- HyDE
- multi-hop retrieval
- contextual retrieval

---

## Chunking

- fixed length
- sentence
- recursive
- semantic
- structural
- parent-child
- proposition-level
- hierarchical

The important question is:

> How do we prove that a chunking strategy improved system performance?

---

## Context Engineering

- context budgeting
- prompt organization
- dynamic context
- context compression
- long context vs RAG
- semantic memory
- episodic memory
- procedural memory
- working memory
- persistent memory
- memory poisoning
- provenance

---

## Reading

### AI Engineering

Chapter 5:

- Context Length
- Context Efficiency
- Breaking Complex Tasks into Subtasks
- Prompt Organization / Versioning

Chapter 6:

- RAG Architecture
- Retrieval Algorithms
- Retrieval Optimization
- RAG Beyond Text

Anthropic:

https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

---

## Lab 2
### Retrieval Ablation Study

Compare:

1. BM25
2. vector retrieval
3. hybrid retrieval
4. hybrid + reranker
5. long-context / no-RAG baseline

Metrics:

- Recall@5
- Recall@10
- MRR
- NDCG
- context precision
- answer correctness
- latency
- token cost

---

## Assignment 2

Research memo:

> When should an engineering team stop improving RAG and use long context instead?

Discuss:

- retrieval quality
- context size
- latency
- cost
- engineering complexity
- failure modes

---

## Quiz 2

1. Why can embeddings retrieve semantically relevant but operationally irrelevant chunks?
2. What problem does reranking solve?
3. Why can BM25 outperform embeddings on certain queries?
4. Difference between retrieval recall and final-answer accuracy?
5. Why can more context reduce answer quality?
6. Difference between memory and retrieval?

---

## Week 2 Artifact

```text
02-retrieval-ablation/
```

---

# WEEK 3
# Agent Engineering From First Principles + MCP

## Goals

Understand agent mechanics before using frameworks.

---

## Topics

### Agent model

- observation
- state
- policy
- action
- environment
- tool
- termination
- budget
- recovery

---

## Agent Patterns

- ReAct
- router
- sequential workflow
- evaluator-optimizer
- reflection
- planner-executor
- supervisor-worker
- state machine
- DAG
- agent-as-tool

---

## Tool Engineering

- tool schemas
- typed arguments
- idempotency
- retries
- timeouts
- side effects
- transaction boundaries
- least privilege
- reversible operations
- irreversible operations

---

## MCP

- host
- client
- server
- tools
- resources
- prompts
- stdio
- Streamable HTTP
- schemas
- authorization
- capability discovery
- error handling

---

## Reading

AI Engineering Chapter 6:

- Agent Overview
- Tools
- Planning
- Failure Modes
- Memory

Research:

- ReAct
- WebShop

MCP:

https://modelcontextprotocol.io/specification/2025-06-18

---

## Lab 3A
### Build Your Own Agent Runtime

Implement from scratch:

```python
while budget_available:
    context = build_context(state)
    decision = model(context)
    action = validate(decision)
    observation = execute(action)
    state.update(observation)

    if complete(state):
        break
```

Add:

- max steps
- timeout
- retry
- structured state
- validation
- tool failures
- human escalation

Then recreate the same system with:

- PydanticAI
or
- another lightweight agent framework

---

## Lab 3B
### MCP Client + MCP Server

Server tools:

```text
search_documents()
fetch_document()
calculate_metric()
store_result()
```

Client should:

- discover tools
- inspect schemas
- invoke tools
- validate responses
- reject malformed output
- handle failures

---

## Assignment 3
### Architecture Decision Record

Question:

> Should this application use an agent?

Compare:

- deterministic workflow
- state machine
- tool-calling LLM
- autonomous agent

A valid high-quality conclusion may be:

> Do not use an agent.

---

## Quiz 3

1. When does a workflow become agentic?
2. Why should side-effect tools be idempotent?
3. What happens if a request times out after a side effect succeeded?
4. Why do tool descriptions affect reliability?
5. What security boundary does MCP create?
6. Why should agents have execution budgets?

---

## Week 3 Artifact

```text
03-agent-runtime-mcp/
```

---

# WEEK 4
# Planning, Compound AI & Multi-Agent Systems

## Goals

Understand when multi-agent architectures help and when they only add complexity.

---

## Topics

### Planning

- task decomposition
- plan-and-execute
- replanning
- hierarchical planning
- graph execution
- state machines
- DAG orchestration
- reflection
- verification

---

## Multi-Agent Architectures

```text
Router → Specialist

Supervisor → Workers

Planner → Executors

Agent → Agent-as-tool

Parallel Agents → Synthesizer

Researcher → Critic → Writer
```

---

## Coordination Problems

- context isolation
- communication overhead
- cascading errors
- coordination failures
- deadlocks
- disagreement
- consensus
- failure propagation
- debugging complexity

---

## Reading

Berkeley:

https://rdi.berkeley.edu/llm-agents/f24

Topics:

- Compound AI Systems
- Multi-Agent Systems
- Software Agents
- Agent Frameworks

Papers:

- AutoGen
- StateFlow
- SWE-agent

---

## Lab 4
### Is Multi-Agent Actually Better?

Implement the same task three times:

### Version A
Single agent

### Version B
Planner → executor

### Version C
Supervisor + specialist agents

Measure:

- success rate
- latency
- number of model calls
- token usage
- errors
- reproducibility
- debugging complexity

Students must justify which architecture should be deployed.

---

# PROJECT 1
# Evidence-First Deep Research Platform

Project duration:

**Weeks 1–4**

The project should simulate a professional research system for:

- consulting
- investment research
- due diligence
- competitive intelligence
- engineering research

---

## Business Problem

User asks:

> Investigate Company X's competitive position, identify contradictory evidence, and prepare an evidence-backed research report.

---

## High-Level Architecture

```text
User
  ↓
Research Planner
  ↓
┌────────────────────────────┐
│ Web Search                 │
│ RAG                        │
│ Repository / Data Tools    │
└───────────┬────────────────┘
            ↓
        MCP Layer
            ↓
      Evidence Store
            ↓
      Research Agent
            ↓
Contradiction Detection
            ↓
 Verification Agent
            ↓
      Cited Report
```

---

## Project 1 Guided Stages

### Stage 1 — Evaluation first

Create:

**80–100 evaluation questions**

Categories:

- direct factual
- multi-source
- temporal
- contradictory
- ambiguous
- missing-answer
- adversarial

---

### Stage 2 — Data ingestion

Support:

- webpages
- PDFs
- structured data
- repository files

Normalized structure:

```text
source_id
title
author
timestamp
content
url
trust_metadata
```

---

### Stage 3 — Retrieval

Implement:

- BM25
- embeddings
- hybrid retrieval
- reranking

Preserve provenance.

---

### Stage 4 — Research planning

Planner returns:

```text
ResearchQuestion
SubQuestions[]
SearchStrategy[]
RequiredEvidence[]
CompletionCriteria[]
```

---

### Stage 5 — MCP

Expose research capabilities through custom MCP tools.

---

### Stage 6 — Evidence Graph

Example:

```text
Claim
 ├── supports → Source A
 ├── supports → Source B
 └── contradicts → Source C
```

---

### Stage 7 — Verification

Verifier output:

```text
SUPPORTED
PARTIALLY_SUPPORTED
CONTRADICTED
INSUFFICIENT_EVIDENCE
```

Verifier should not write the final report.

---

### Stage 8 — Final Report

Every material claim should retain provenance.

---

### Stage 9 — Evaluation

Measure:

- Recall@K
- citation precision
- citation completeness
- unsupported-claim rate
- tool-selection accuracy
- planner success
- latency
- token use

---

### Stage 10 — Architecture Experiment

Compare:

```text
Single Research Agent
```

against

```text
Planner + Researcher + Verifier
```

Multi-agent stays only if results justify complexity.

---

## Project 1 Deliverables

```text
project-1/
├── src/
├── mcp/
├── retrieval/
├── agents/
├── evals/
├── tests/
├── experiments/
├── docker/
├── architecture.md
├── evaluation_report.md
└── README.md
```

Plus:

- architecture diagram
- evaluation report
- design document
- failure analysis
- 5-minute demo

---

# WEEK 5
# Reliability, Security & Agent Evaluation

## Goals

Move from:

> "The agent worked."

to:

> "The system is measurable, permissioned, resilient, and defensible."

---

## Topics

### Agent Evaluation

Evaluate separately:

```text
Request
  ↓
Intent
  ↓
Retrieval
  ↓
Planning
  ↓
Tool Selection
  ↓
Tool Arguments
  ↓
Execution
  ↓
Trajectory
  ↓
Final Answer
```

Metrics:

- task success
- tool accuracy
- argument correctness
- trajectory efficiency
- unnecessary actions
- retry rate
- recovery rate
- human escalation

---

## Security

Study:

- direct prompt injection
- indirect prompt injection
- tool poisoning
- memory poisoning
- RAG poisoning
- secret leakage
- excessive agency
- privilege escalation
- malicious MCP servers
- SSRF
- data exfiltration

OWASP:

https://genai.owasp.org/llm-top-10/

---

## Lab 5
### Red-Team the Agent

Create:

**≥50 attacks**

Examples:

- direct prompt injection
- malicious webpage instruction
- poisoned document
- malicious tool argument
- unauthorized destructive action
- secret extraction
- infinite loop attempt

Implement:

```text
Input Validation
      +
Context Isolation
      +
Tool Permissions
      +
Least Privilege
      +
Output Validation
      +
Human Approval
      +
Audit Logging
```

---

## Assignment 5
### Incident Postmortem

Scenario:

> Agent success rate fell from 91% to 68% after deployment.

Diagnose:

- model
- prompt
- retrieval
- data
- tool
- orchestration

Write:

- incident timeline
- evidence
- root cause
- corrective actions
- preventive controls

---

## Quiz 5

1. Why does a stronger system prompt not solve prompt injection?
2. What is excessive agency?
3. Why should tool output be treated as untrusted?
4. What is retrieval poisoning?
5. Where should human approval happen?
6. Explain least privilege for agents.

---

## Week 5 Artifact

```text
05-agent-reliability/
```

---

# WEEK 6
# Fine-Tuning, Dataset Engineering & Inference

## Goals

Understand enough model adaptation and inference engineering to make correct architecture decisions.

---

## Part A — Fine-Tuning

### Reading

AI Engineering Chapter 7:

- When to Fine-Tune
- Reasons to Fine-Tune
- Reasons Not to Fine-Tune
- Fine-Tuning + RAG
- Quantization
- Parameter-Efficient Fine-Tuning

---

## Topics

- SFT
- LoRA
- QLoRA
- adapters
- quantization
- catastrophic forgetting
- domain adaptation
- RAG vs fine-tuning

---

## Part B — Dataset Engineering

### Reading

AI Engineering Chapter 8:

- data quality
- coverage
- quantity
- annotation
- synthetic data
- distillation
- deduplication
- filtering
- cleaning

---

## Part C — Inference Engineering

### Reading

AI Engineering Chapter 9:

- inference performance
- model optimization
- serving optimization

Topics:

- TTFT
- tokens/sec
- throughput
- concurrency
- batching
- continuous batching
- KV cache
- prefix caching
- quantization
- speculative decoding
- model routing
- GPU utilization

---

## Lab 6A
### Adaptation Study

Compare:

1. zero-shot
2. few-shot
3. advanced prompt
4. RAG
5. LoRA
6. LoRA + RAG

Use one common evaluation harness.

---

## Lab 6B
### Inference Benchmark

Benchmark:

```text
Concurrent Users
vs
Throughput
vs
TTFT
vs
p95 latency
vs
memory
```

Test at least one optimization.

---

## Assignment 6

Design infrastructure for:

```text
100 requests/second
p95 latency < 2 seconds
```

Specify:

- model
- quantization
- GPU assumptions
- batching
- cache
- autoscaling
- fallback
- capacity margin

---

## Quiz 6

1. Why does fine-tuning not reliably add rapidly changing knowledge?
2. What problem does LoRA solve?
3. What is KV cache?
4. Why can batching hurt latency while improving throughput?
5. Difference between TTFT and total latency?
6. When should RAG and fine-tuning be combined?

---

## Week 6 Artifact

```text
06-adaptation-inference/
```

---

# WEEK 7
# Production Architecture, Durable Workflows & Observability

## Goals

Turn agents into production software systems.

---

## Production Architecture

Study:

- API gateway
- model gateway
- model router
- semantic cache
- rate limiter
- queues
- persistence
- provider fallback
- secrets
- feature flags
- canary
- rollback

---

## Durable Workflows

Study:

- cron
- webhooks
- queues
- events
- DAGs
- durable execution
- checkpoints
- retries
- compensation
- idempotency
- long-running workflows
- human approval
- dead-letter queues

Automation tools:

- Python
- n8n
- optionally Temporal / Restate / Dapr concepts

---

## Observability

Study:

- logs
- metrics
- traces
- spans
- OpenTelemetry
- distributed tracing
- model calls
- tool calls
- latency
- token use
- retries
- failures
- cost attribution
- SLA
- SLO

---

## Lab 7
### Durable AI Workflow

Build:

```text
Scheduled / Event Trigger
        ↓
       Queue
        ↓
   Data Ingestion
        ↓
Deterministic Validation
        ↓
       Agent
        ↓
 Verification
        ↓
 Human Approval
        ↓
 External Action
        ↓
 Audit Trail
```

Inject:

- service failure
- duplicate event
- timeout
- process restart

System must recover correctly.

---

## Assignment 7
### Production Architecture RFC

Include:

- component diagram
- sequence diagram
- failure modes
- SLOs
- security boundary
- scaling strategy
- observability
- deployment strategy
- rollback

---

## Quiz 7

1. What makes workflow execution durable?
2. Why must event handlers be idempotent?
3. Difference between retry and compensation?
4. Why use queues around agent systems?
5. What is a model gateway?
6. What should one distributed agent trace include?

---

## Week 7 Artifact

```text
07-production-platform/
```

---

# WEEK 8
# Senior AI System Design & Production Defense

## Goals

Integrate everything into production-level system design.

---

## Reliability

- SLI
- SLO
- SLA
- tail latency
- circuit breaker
- fallback
- graceful degradation
- rate limiting
- load shedding
- chaos testing
- failure budgets

---

## AI Economics

Trade-off:

```text
         Quality
           ↑
           |
Cost ←────────────→ Latency
```

Study:

- small model routing
- escalation
- local vs hosted models
- caching
- prompt compression
- retrieval compression
- cost attribution

---

## Continuous Improvement

```text
Production
   ↓
Telemetry
   ↓
Failure Cases
   ↓
Evaluation Dataset
   ↓
Experiments
   ↓
Candidate Release
   ↓
Canary
   ↓
Production
```

---

## Lab 8
### Chaos Engineering for Agents

Break the system deliberately.

Test:

- LLM unavailable
- vector DB down
- MCP server down
- malformed model output
- high latency
- incorrect tool value
- poisoned document
- token budget exhausted
- approval never arrives

Measure degradation.

---

## Oral Systems Exam

Student must defend:

1. RAG or long context?
2. Workflow or agent?
3. One agent or multiple agents?
4. Prompting or fine-tuning?
5. Hosted or local model?
6. How do you know retrieval is the bottleneck?
7. How should agents be evaluated?
8. How do you secure tool use?
9. How do you detect production drift?
10. How would you halve cost with minimal quality loss?

---

# PROJECT 2
# Customer Intelligence & Campaign Operations Platform

Weeks 5–8. See /projects/2/ for the complete guided build, UCI dataset, evaluation, approval workflow, and technical defense.

# 12. Final Repository Standard

Both projects should look like professional engineering repositories.

```text
project/
├── src/
│   ├── agents/
│   ├── retrieval/
│   ├── tools/
│   ├── workflows/
│   └── api/
├── mcp/
├── evals/
├── tests/
├── security/
├── experiments/
├── monitoring/
├── infra/
├── docker-compose.yml
├── architecture.md
├── evaluation_report.md
├── SECURITY.md
├── Makefile
└── README.md
```

Avoid final deliverables that are only:

```text
final_notebook.ipynb
```

---

# 13. Reading Map by Week

| Week | Reading |
|---|---|
| 1 | AI Engineering Ch. 2–4 |
| 2 | Ch. 5 + RAG sections of Ch. 6 |
| 3 | Agent/tools/planning/memory sections of Ch. 6 |
| 4 | Berkeley compound AI + AutoGen + StateFlow + SWE-agent |
| 5 | Defensive prompting + OWASP + MCP security |
| 6 | AI Engineering Ch. 7–9 |
| 7 | Ch. 10 + OpenTelemetry + LLMOps |
| 8 | Ch. 10 revisit + reliability/economics + final report |

---

# 14. Website Idea

The curriculum should ultimately become an interactive course website.

Main design reference:

https://aiengineeringfromscratch.com/

Desired characteristics:

- technical
- minimal
- academic
- modern
- no unnecessary visual clutter
- curriculum-first
- structured around modules
- progress visible
- clear weekly hierarchy
- dedicated lab pages
- dedicated quiz pages
- dedicated assignment pages
- dedicated project pages
- persistent progress in browser
- polished desktop and mobile experience

---

# 15. Recommended Website Structure

```text
/
├── Home
├── Curriculum
│   ├── Week 1
│   ├── Week 2
│   ├── Week 3
│   ├── Week 4
│   ├── Week 5
│   ├── Week 6
│   ├── Week 7
│   └── Week 8
│
├── Labs
│   ├── Lab 01
│   ├── Lab 02
│   ├── ...
│   └── Lab 08
│
├── Assignments
│   ├── Assignment 01 — Model Selection RFC
│   ├── Assignment 02 — RAG vs Long Context
│   ├── Assignment 03 — Workflow vs Agent ADR
│   ├── Assignment 05 — Incident Postmortem
│   ├── Assignment 06 — Inference Architecture
│   └── Assignment 07 — Production Architecture RFC
│
├── Quizzes
│   ├── Quiz 01
│   └── ...
│
├── Projects
│   ├── Project 01 — Deep Research Platform
│   └── Project 02 — Customer Intelligence Platform
│
├── Reading
├── Progress
└── About
```

---

# 16. Suggested Homepage

Hero:

```text
ADVANCED AI SYSTEMS ENGINEERING

From RAG and evaluation
to agents, MCP, inference,
security and production systems.

8 weeks
18–25 hrs/week
8 labs
8 quizzes
2 advanced projects
```

CTA:

```text
Start the Course
Explore Curriculum
View Capstones
```

---

# 17. Suggested Week Page

Example:

```text
Week 03
Agent Engineering From First Principles

Learning Objectives
Lecture Topics
Required Reading
Research Papers
Lab 03A
Lab 03B
Assignment
Quiz
Artifact
Completion Status
```

---

# 18. Suggested Assignment Page

Each assignment page should contain:

- scenario
- business context
- objective
- constraints
- required work
- deliverables
- rubric
- technical defense questions
- submission format

Example:

## Assignment 01 — Model Selection RFC

Scenario:

> Build the production model strategy for a knowledge agent handling 500,000 monthly queries.

Required:

- 3 model strategies
- benchmark
- cost analysis
- latency analysis
- reliability strategy
- fallback
- architecture diagram
- ≤1,500-word RFC

---

# 19. Suggested Lab Page

Each lab should contain:

```text
Lab Number
Estimated Time
Prerequisites
Learning Goal
System Diagram
Implementation Tasks
Experiments
Required Metrics
Expected Failure Cases
Submission Artifact
Stretch Goal
```

---

# 20. Suggested Quiz Design

Quizzes should **not** be simple multiple choice.

Use:

- short explanations
- architecture judgment
- debugging
- scenario analysis
- metric selection
- security reasoning

Example:

> An agent calls the same payment tool twice after a network timeout. Explain the likely systems-design flaw and how you would fix it.

---

# 21. Suggested Project Pages

Project pages should be extensive guided builds.

Each should include:

- business problem
- architecture
- weekly milestones
- technical requirements
- datasets
- system components
- evaluation requirements
- security requirements
- failure cases
- deployment
- observability
- project rubric
- technical report template
- demo checklist

---

# 22. Progress System

The site should allow users to track:

- week completion
- lab completion
- quiz completion
- assignment completion
- project milestones

At minimum use:

```text
localStorage
```

Later optionally support:

- user accounts
- database persistence
- login

But keep the first version free and local-first.

---

# 23. Visual Style

The site should feel:

- serious
- technical
- engineering-oriented
- minimal
- premium
- research-course-like

Avoid:

- cartoon illustrations
- generic SaaS gradients everywhere
- over-designed cards
- excessive rounded corners
- marketing-heavy language

Prefer:

- strong typography
- monospace labels
- section numbering
- technical diagrams
- structured grids
- subdued neutral palette
- one strong accent color
- architecture drawings

---

# 24. Conversation Summary

This project evolved through the following decisions.

## Initial Request

The original goal was to create a free equivalent of:

https://maven.com/alexey-grigorev/from-rag-to-agents

within approximately:

**4–6 weeks**

for a learner who already completed LLM Zoomcamp.

Requirements included:

- YouTube
- GitHub
- readings
- articles
- free resources
- agent workflows
- automation

---

## Curriculum Upgrade

The scope was then raised substantially.

The user requested:

- advanced level
- MIT / Stanford-style rigor
- senior AI engineer outcome
- AI Engineering book readings
- deeper theory
- labs
- assignments
- quizzes
- production engineering

Additional course references were added:

https://aiengineeringfromscratch.com/

https://rdi.berkeley.edu/llm-agents/f24

---

## Duration Change

The course was expanded from:

```text
4–6 weeks
```

to:

```text
8 weeks
```

to allow deeper coverage.

---

## Assessment Expansion

The course was expanded to include:

- weekly quizzes
- weekly labs
- assignments
- architecture memos
- research readings
- project milestones
- final technical defense

---

## Project Requirement

Two full guided, advanced, end-to-end projects were added:

### Project 1
Evidence-First Deep Research Platform

### Project 2
Customer Intelligence & Campaign Operations Platform

---

## Website Requirement

The final course should be converted into an interactive site.

The main design / UX reference is:

https://aiengineeringfromscratch.com/

The website should be inspired by its:

- structure
- clarity
- course navigation
- technical style
- modularity
- progress experience

but should remain visually and structurally original.

---

# 25. Existing Prototype

A first static prototype was created with:

```text
index.html
assignment-1.html
styles.css
script.js
README.md
```

It included:

- curriculum homepage
- expandable weeks
- progress tracking
- project sections
- assessment
- reading map
- dedicated Assignment 01 page

When rebuilding in ChatGPT Work, this prototype may be used as reference, but the preferred output is a more complete site with dedicated pages for all course artifacts.

---

# 26. What ChatGPT Work Should Build

Use this document as the main specification.

Build a production-quality course website that includes:

## Phase 1

- homepage
- curriculum page
- all 8 week pages
- both project pages
- reading page
- progress tracker

## Phase 2

Create dedicated pages for:

- every lab
- every quiz
- every assignment
- both capstones

## Phase 3

Add:

- diagrams
- architecture visuals
- navigation
- completion states
- persistent local progress
- responsive design

Optional:

- search
- dark mode
- downloadable assignment briefs
- downloadable project templates

---

# 27. Course Quality Standard

Do not turn this into:

> "Watch video → clone repo → done."

Every module should include:

- conceptual understanding
- implementation
- comparison
- measurement
- failure analysis
- artifact

---

# 28. Senior-Level Questions the Course Must Prepare Students to Answer

A student who finishes should be able to answer and defend:

### Retrieval

- Why RAG instead of long context?
- Why BM25 + vector instead of vector alone?
- Why rerank top 50 and return top 5?
- How do you know retrieval is the bottleneck?

### Agents

- Why an agent instead of a workflow?
- Why multiple agents instead of one?
- What happens after a tool times out?
- What if the side effect already succeeded?
- How do you control agent permissions?

### Evaluation

- How was the evaluation set constructed?
- How was the judge calibrated?
- How do you detect regression?
- What is the confidence interval?

### Security

- What happens if retrieved content contains malicious instructions?
- How do you prevent data exfiltration?
- How are MCP tools permissioned?

### Inference

- What are p50 / p95 / p99 targets?
- What is TTFT?
- How do you reduce cost?
- When is quantization appropriate?
- Why might batching harm latency?

### Architecture

- How do you roll back?
- What happens if the model provider fails?
- What should be cached?
- Where should a queue exist?
- Which operations require approval?
- How does observability trace one request end-to-end?

### Model Adaptation

- When should you fine-tune?
- When should you not?
- When should fine-tuning and RAG be combined?

---

# 29. Final Principle

The most important philosophy for the entire course:

> **Do not organize the course around frameworks. Organize it around engineering problems.**

Frameworks will change.

The enduring skills are:

- evaluation
- retrieval
- architecture
- planning
- reliability
- security
- inference
- observability
- workflow orchestration
- production judgment

---

# 30. Primary Links Summary

## Course References

- Alexey Grigorev — From RAG to Agents  
  https://maven.com/alexey-grigorev/from-rag-to-agents

- AI Engineering from Scratch  
  https://aiengineeringfromscratch.com/

- Berkeley LLM Agents  
  https://rdi.berkeley.edu/llm-agents/f24

---

## Book

- AI Engineering companion repository  
  https://github.com/chiphuyen/aie-book

- AI Engineering table of contents  
  https://github.com/chiphuyen/aie-book/blob/main/ToC.md

---

## Agents / Context

- Anthropic — Building Effective Agents  
  https://www.anthropic.com/engineering/building-effective-agents

- Anthropic — Effective Context Engineering  
  https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

- PydanticAI  
  https://github.com/pydantic/pydantic-ai

- PydanticAI Docs  
  https://ai.pydantic.dev/

- OpenAI Agents SDK  
  https://github.com/openai/openai-agents-python

- OpenAI Agents SDK Docs  
  https://openai.github.io/openai-agents-python/

---

## MCP

- MCP Specification  
  https://modelcontextprotocol.io/specification/2025-06-18

- MCP Python SDK  
  https://github.com/modelcontextprotocol/python-sdk

---

## Operations / Evaluation

- Full Stack Deep Learning  
  https://fullstackdeeplearning.com/llm-bootcamp/

- OpenTelemetry  
  https://opentelemetry.io/docs/

- Grafana  
  https://grafana.com/docs/

- Evidently  
  https://docs.evidentlyai.com/

---

## Security

- OWASP GenAI Top 10  
  https://genai.owasp.org/llm-top-10/

---

## Inference

- vLLM  
  https://docs.vllm.ai/

---

## Workflow Automation

- n8n Self-Hosted AI Starter Kit  
  https://github.com/n8n-io/self-hosted-ai-starter-kit

---

# 31. Prompt to Give ChatGPT Work

You can provide this file to ChatGPT Work and use the prompt below:

> Build a complete production-quality course website from the attached `advanced_ai_systems_engineering_curriculum.md`.
>
> Use the full curriculum and preserve its academic rigor, weekly structure, labs, quizzes, assignments, reading list, and both guided projects.
>
> The main UX and design inspiration is:
> https://aiengineeringfromscratch.com/
>
> Do not copy the site's branding or source code. Create an original technical/academic design with similar clarity and curriculum-first navigation.
>
> Requirements:
>
> - Responsive website
> - Homepage
> - 8 dedicated week pages
> - dedicated pages for each lab
> - dedicated pages for each quiz
> - dedicated pages for each assignment
> - dedicated pages for both capstone projects
> - reading/resources page
> - local progress tracking
> - clear navigation
> - technical diagrams
> - strong typography
> - minimal academic / engineering visual style
> - runnable locally without paid services
>
> Use the curriculum file as the source of truth.
>
> Where a section would benefit from richer content, expand it using the linked official course, book companion, research, documentation, or primary sources while preserving the original learning goals and rigor.
>
> Do not simplify this into a beginner course.
>
> The final output should feel like a serious graduate-level AI systems engineering course that could credibly prepare a strong LLM Zoomcamp graduate for senior-level AI engineering project work.

---

# 32. Final Handoff Note

This Markdown file should be treated as the canonical specification.

The website implementation may improve:

- layout
- interactivity
- diagrams
- navigation
- content presentation

but should **not weaken the curriculum**.

The course should remain:

- advanced
- evidence-driven
- evaluation-first
- implementation-heavy
- systems-oriented
- production-aware
- security-aware
- project-driven


# Edition 03 learning contract

52 ordered learning units; 10 guided labs; 64 independent scenarios; 176 planned hours. Required videos have complete written access routes. Retrieval retains six configurations: BM25-only, vector-only, hybrid, hybrid plus reranking, document-tree, long-context. Adaptation retains zero-shot, few-shot, advanced prompting, RAG, LoRA, LoRA plus RAG. See /syllabus/ for workload and evidence standards and /projects/2/ for the authorized customer-intelligence project.
