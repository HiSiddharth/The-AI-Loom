# AI Loom Architecture Specification

# Chapter 19 — Development Roadmap & Implementation Plan

**Version:** 1.0 Draft

---

# 19.1 Purpose

This chapter converts the architecture into an executable engineering plan.

The objective is not merely to build AI Loom.

The objective is to build it in an order where every milestone produces a usable, testable system.

Each phase should leave the project in a deployable state.

---

# 19.2 Development Philosophy

Development follows these principles:

* Build vertically, not horizontally.
* Every phase should produce working software.
* Optimise for correctness before optimisation.
* Introduce complexity only when required.
* Measure before improving.

The roadmap deliberately postpones advanced features until the foundation is stable.

---

# 19.3 High-Level Roadmap

```text
Foundation

↓

Single Worker Agent

↓

Planner

↓

Context Engine

↓

Indexer

↓

Validation

↓

Memory

↓

Multi-Model Routing

↓

Observability

↓

Plugins

↓

Distributed Runtime

↓

AI Loom v1.0
```

Each stage depends only on previous stages.

---

# 19.4 Phase 0 — Project Bootstrap

Duration:

1–2 days

Deliverables:

* Repository
* Project structure
* Configuration loader
* Logging
* Dependency injection
* Event bus
* CLI skeleton
* Unit testing framework

Success Criteria:

```text
ailoom --help

works.
```

No AI yet.

---

# 19.5 Phase 1 — Tool Engine

Implement:

* File reading
* File writing
* Search
* Terminal execution
* Permission manager

Success:

```text
Worker

↓

Tool Engine

↓

Filesystem
```

All tools fully tested.

No LLM required.

---

# 19.6 Phase 2 — Single Worker Agent

Implement:

* One Worker
* One model
* Tool calling
* Retry logic
* Structured outputs

Success:

```text
Implement login endpoint.
```

Worker edits repository correctly.

No Planner.

---

# 19.7 Phase 3 — Repository Indexer

Implement:

* Tree-sitter
* Symbol graph
* Dependency graph
* Incremental indexing

Worker now uses indexed retrieval.

Repository scale increases dramatically.

---

# 19.8 Phase 4 — Context Engine

Implement:

* Retrieval
* Ranking
* Compression
* Prompt assembly
* Token budgeting

Worker stops reading entire files.

Context becomes intelligent.

---

# 19.9 Phase 5 — Planner

Replace:

```text
User

↓

Worker
```

with:

```text
User

↓

Planner

↓

Worker
```

Planner produces task graph.

Worker remains unchanged.

---

# 19.10 Phase 6 — Validation

Implement:

* Compilation
* Tests
* Linting
* Reviewers

Workers can no longer declare success.

Validation becomes mandatory.

---

# 19.11 Phase 7 — Memory

Implement:

* Project memory
* Session memory
* Architectural decisions
* Lessons learned

Planner becomes progressively smarter across long sessions.

---

# 19.12 Phase 8 — Model Router

Replace:

```text
Worker

↓

Model
```

with:

```text
Worker

↓

Router

↓

Provider

↓

Model
```

Planner and Worker now request capabilities instead of models.

---

# 19.13 Phase 9 — Observability

Implement:

* Event bus
* Timeline
* Metrics
* Dashboard
* Tracing

Debugging becomes dramatically easier.

---

# 19.14 Phase 10 — Plugin System

Convert:

* Providers
* Validators
* Languages
* Frameworks

into plugins.

Core size decreases.

Extensibility increases.

---

# 19.15 Phase 11 — Runtime

Implement:

* Daemon
* Multiple sessions
* Health checks
* Recovery
* APIs

CLI becomes a thin client.

---

# 19.16 Phase 12 — Distributed Execution

Optional.

Move:

```text
Worker
```

to:

```text
Remote Machine
```

No Planner changes required.

---

# 19.17 Parallel Work

Some components may be developed independently.

Examples:

| Component           | Depends On  |
| ------------------- | ----------- |
| Tool Engine         | Runtime     |
| Tree-sitter Indexer | Runtime     |
| Validation          | Tool Engine |
| Provider Plugins    | Router      |
| Dashboard           | Event Bus   |

This enables future contributors.

---

# 19.18 Suggested Repository Layout

```text
ailoom/

├── api/
├── cli/
├── config/
├── context/
├── core/
├── events/
├── indexer/
├── memory/
├── planner/
├── plugins/
├── providers/
├── routing/
├── runtime/
├── security/
├── tools/
├── validation/
├── workers/
├── tests/
└── docs/
```

Every package has a single responsibility.

---

# 19.19 Milestone Definitions

## Milestone A

Usable coding assistant.

Features:

* Single Worker
* Tool Engine
* Local model

Equivalent to a basic coding agent.

---

## Milestone B

Scalable coding assistant.

Features:

* Planner
* Context Engine
* Indexer

Large repositories become practical.

---

## Milestone C

Reliable coding assistant.

Features:

* Validation
* Reviewers
* Memory

Quality becomes significantly higher.

---

## Milestone D

Intelligent orchestration.

Features:

* Multi-model routing
* Observability
* Plugins

System becomes flexible and maintainable.

---

## Milestone E

AI Loom v1.0

Features:

* Complete runtime
* Distributed-ready architecture
* Stable APIs
* Plugin ecosystem

---

# 19.20 Technical Debt Policy

Every TODO must include:

* Reason
* Owner
* Priority
* Planned milestone

No anonymous technical debt.

---

# 19.21 Coding Standards

Core principles:

* Strong typing
* Small modules
* Constructor injection
* No circular dependencies
* Comprehensive tests
* Clear interfaces

Prefer readability over cleverness.

---

# 19.22 Testing Strategy

Every phase must include:

* Unit tests
* Integration tests
* Performance benchmarks (where appropriate)

Architecture changes require regression testing.

---

# 19.23 Documentation Strategy

Documentation evolves with the codebase.

Maintain:

* Architecture
* APIs
* Plugin guide
* Configuration reference
* Contributor guide

Documentation is treated as code.

---

# 19.24 Performance Goals

Target (local workstation):

| Operation           |   Target |
| ------------------- | -------: |
| Startup             |    < 2 s |
| Index 100k LOC      |   < 10 s |
| Context Retrieval   | < 100 ms |
| Planner Response    |    < 5 s |
| Worker Tool Call    | < 200 ms |
| Validation Dispatch | < 100 ms |

Model inference is excluded.

---

# 19.25 Risks

Major engineering risks:

* Poor retrieval quality
* Context overflow
* Tool reliability
* Model inconsistency
* Slow indexing
* Excessive orchestration overhead

Each should have dedicated benchmarks.

---

# 19.26 Success Metrics

AI Loom succeeds if it can:

* Understand large repositories.
* Solve multi-step engineering tasks.
* Recover from failures.
* Explain every decision.
* Validate all changes.
* Switch models transparently.
* Resume interrupted work.
* Operate for hours without degrading.

---

# 19.27 Versioning Strategy

Recommended:

```text
0.1

↓

0.2

↓

0.5

↓

0.9

↓

1.0
```

Avoid premature API stability before 1.0.

---

# 19.28 Release Process

Every release should include:

* Automated tests
* Benchmark comparison
* Documentation update
* Changelog
* Migration notes (if applicable)

Releases should be reproducible.

---

# 19.29 Future Research Areas

Potential AI Loom v2 research:

* Multi-agent collaboration
* Self-improving retrieval
* Autonomous benchmarking
* Learned routing policies
* Distributed planning
* Voice interaction
* Long-term project memory
* Formal verification
* Reinforcement learning from developer feedback

These are intentionally outside the scope of v1.

---

# 19.30 Design Constraints

1. Every milestone produces usable software.
2. Architecture precedes optimisation.
3. Interfaces stabilise before implementations.
4. Components remain independently testable.
5. Complexity grows gradually.
6. Every subsystem has benchmarks.
7. Documentation stays current.
8. Plugin APIs remain backwards compatible after v1.0.
9. Performance regressions are tracked.
10. AI Loom v1.0 remains fully usable offline with supported local providers.

---

# Architect's Notes (Normative)

## 1. Build the Simplest Thing That Can Possibly Work

Resist the temptation to implement every architectural idea immediately.

For example:

* First implement one Worker.
* Then multiple Workers.
* Then a Planner.
* Then routing.

Each stage should replace an implementation, not redesign the architecture.

---

## 2. Benchmark Continuously

Before optimising, establish baselines.

Measure:

* Indexing speed
* Context retrieval latency
* Model throughput
* Validation time
* End-to-end task completion

Keep historical benchmark results in the repository to detect regressions.

---

## 3. Favour Interfaces Early

Even when only one implementation exists, define interfaces for:

* Indexer
* Provider
* Memory Store
* Validator
* Planner
* Tool

This keeps future replacements straightforward.

---

## 4. Treat Documentation as Part of the Product

The architecture document, API documentation and contributor guide should evolve alongside the implementation.

New contributors should be able to understand the system without reverse-engineering the code.

---

## 5. Suggested MVP for Your Hardware

Given your RTX 4060 (8 GB VRAM) and your planned workflow, the most practical initial version is:

```text
User

↓

Planner (Qwen 3.6 27B)

↓

Task Queue

↓

Single Worker (Qwen 3.5 9B)

↓

Tool Engine

↓

Validation

↓

Planner Review

↓

Done
```

Do **not** implement:

* Distributed execution
* Multiple concurrent Workers
* Plugin marketplace
* Adaptive learning
* Remote execution

until this pipeline is reliable.

This MVP already aligns with your original goal:

* Heavy reasoning is delegated to the 27B model.
* Fast implementation work is handled by the 9B model in fresh contexts.
* Validation provides deterministic confidence before completion.
* The architecture remains extensible without premature complexity.

---

**End of Chapter 19**
