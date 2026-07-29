# AI Loom Architecture Specification

# Chapter 20 — AI Loom v1.0 Technical Specification (Normative)

**Version:** 1.0 Draft

---

# 20.1 Purpose

This chapter defines the **mandatory requirements** for AI Loom v1.0.

Previous chapters described the architecture.

This chapter specifies what **must** exist before AI Loom can be considered version 1.0.

Anything not listed here is optional.

---

# 20.2 Definition of AI Loom v1.0

AI Loom v1.0 is defined as:

> A local-first, agentic software engineering platform capable of planning, implementing, validating and explaining software changes using multiple LLMs while remaining deterministic, observable and secure.

---

# 20.3 Core Capabilities

The following capabilities are mandatory.

| Capability          | Required |
| ------------------- | -------- |
| Planning            | ✓        |
| Worker Execution    | ✓        |
| Context Retrieval   | ✓        |
| Repository Indexing | ✓        |
| Validation          | ✓        |
| Multi-model Routing | ✓        |
| Tool Execution      | ✓        |
| Permission System   | ✓        |
| Memory              | ✓        |
| Observability       | ✓        |
| Plugin Architecture | ✓        |
| Runtime             | ✓        |

Failure to implement any of these means the project is not AI Loom v1.0.

---

# 20.4 Supported Repository Scale

Minimum supported repository:

```text
100,000+ LOC
```

without requiring the entire repository inside the model context.

---

# 20.5 Supported Languages

Version 1 should officially support:

```text
Python

TypeScript

JavaScript
```

Additional languages are optional plugins.

---

# 20.6 Required Local Providers

AI Loom must support at least one local provider.

Recommended:

```text
LM Studio
```

Optional:

```text
Ollama

llama.cpp

vLLM
```

---

# 20.7 Required Interfaces

Version 1 requires:

```text
CLI

Python API
```

Recommended:

```text
REST API

WebSocket
```

---

# 20.8 Offline Operation

AI Loom must operate fully offline except when:

* User enables network tools
* Cloud provider is configured
* Plugin explicitly requires internet

Offline is the default deployment model.

---

# 20.9 Mandatory Components

Every deployment includes:

```text
Planner

Worker

Model Router

Tool Engine

Context Engine

Indexer

Memory

Validation

Permission Manager

Runtime

Event Bus
```

No optional substitutions.

---

# 20.10 Worker Requirements

Workers must:

* use structured outputs
* retry failed tool calls
* request context when needed
* never bypass permissions
* support cancellation
* produce deterministic reports

---

# 20.11 Planner Requirements

Planner must:

* create task graphs
* prioritise tasks
* coordinate Workers
* invoke validation
* review completed work
* recover from failures

---

# 20.12 Context Engine Requirements

Must support:

* symbol retrieval
* dependency expansion
* token budgeting
* prompt construction
* context compression

---

# 20.13 Index Requirements

Index must provide:

* symbols
* references
* dependency graph
* imports
* file metadata
* incremental updates

---

# 20.14 Validation Requirements

Validation must include:

```text
Compilation

Linting

Tests

Reviewer
```

Compilation is skipped where not applicable.

---

# 20.15 Security Requirements

Mandatory:

* Workspace isolation
* Permission policies
* Path validation
* Audit logging
* Secret protection
* Atomic writes

---

# 20.16 Performance Targets

Recommended targets:

| Operation         |  Target |
| ----------------- | ------: |
| Startup           |    <2 s |
| Context Retrieval | <100 ms |
| Symbol Lookup     |  <20 ms |
| Index Update      | <200 ms |
| Event Publish     |   <1 ms |

Model inference excluded.

---

# 20.17 Memory Requirements

Project memory must persist.

Session memory must expire.

Task memory must be temporary.

Architectural memory must be versioned.

---

# 20.18 Observability Requirements

Every execution must be traceable.

Mandatory:

```text
Timeline

Metrics

Errors

Events

Session History
```

---

# 20.19 Plugin Requirements

Plugin system must support:

* Providers
* Validators
* Languages
* Tools

Everything else may remain built-in initially.

---

# 20.20 Configuration Requirements

Configuration must support:

* profiles
* layered overrides
* environment variables
* workspace configuration

---

# 20.21 Error Recovery

Mandatory recovery:

```text
Model Failure

↓

Fallback

Tool Failure

↓

Retry

Validation Failure

↓

Worker Revision

Permission Denied

↓

Planner Decision
```

---

# 20.22 User Experience

The ideal workflow should feel like:

```text
User

↓

Describe Goal

↓

Planner

↓

Workers

↓

Validation

↓

Summary

↓

Done
```

The user should never need to manually coordinate individual Workers.

---

# 20.23 Deliverables

Version 1 release should include:

* Executable binary or installer
* CLI
* Documentation
* Architecture specification
* Contributor guide
* Plugin guide
* Configuration reference
* API reference

---

# 20.24 Non-Goals

Explicitly excluded from v1.0:

* Self-modifying prompts
* Self-training
* Autonomous internet browsing
* Continuous background coding
* Automatic dependency installation
* Marketplace infrastructure
* Distributed Workers
* Autonomous code deployment

These may be explored in future versions.

---

# 20.25 Acceptance Criteria

AI Loom v1.0 is considered complete when it can successfully perform the following end-to-end workflow on a real project:

1. Index the repository.
2. Understand the user's objective.
3. Generate a task graph.
4. Retrieve only relevant context.
5. Delegate implementation to Workers.
6. Execute required tools.
7. Validate the result.
8. Review the completed implementation.
9. Produce an explanation of the changes.
10. Leave the repository in a valid state.

No manual intervention should be required except for permission approvals where configured.

---

# 20.26 Future Compatibility

Every major subsystem must expose stable interfaces so that future versions can replace implementations without changing public behaviour.

Examples:

* Replace LM Studio with another provider.
* Replace the Planner with a more advanced planning algorithm.
* Replace SQLite with PostgreSQL.

The surrounding architecture should remain unchanged.

---

# 20.27 Reference Implementation

The recommended first implementation stack is:

| Component     | Technology                        |
| ------------- | --------------------------------- |
| Language      | Python 3.12+                      |
| Async Runtime | asyncio                           |
| Models        | LM Studio (OpenAI-compatible API) |
| Parsing       | Tree-sitter                       |
| Storage       | SQLite                            |
| Validation    | Native project tooling            |
| Config        | YAML                              |
| Data Models   | Pydantic                          |
| CLI           | Typer                             |
| Logging       | structlog or standard logging     |
| Testing       | pytest                            |

This is a recommendation, not a requirement.

---

# 20.28 Final Design Principles

Every design decision in AI Loom should be evaluated against these principles:

1. **Local-first**
2. **Deterministic where possible**
3. **Evidence over assumptions**
4. **Composable architecture**
5. **Strong interfaces**
6. **Security by default**
7. **Observable behaviour**
8. **Human remains in control**
9. **Replace implementations, not architecture**
10. **Optimise for long-term maintainability**

---

# 20.29 Vision

AI Loom is **not** intended to be another chatbot with tools.

It is intended to become a software engineering operating system.

Models are interchangeable.

Providers are interchangeable.

Tools are interchangeable.

The architecture is the product.

---

# 20.30 Final Statement

The defining characteristic of AI Loom is not that it uses powerful language models.

Its defining characteristic is that it **orchestrates** specialised components into a reliable engineering workflow.

Planning, retrieval, implementation, validation, memory and security are treated as independent systems cooperating through well-defined interfaces.

As models improve over time, AI Loom should improve automatically—without requiring its core architecture to be redesigned.

---

# Architect's Closing Notes

After reviewing the complete architecture, there is one recommendation I would make for your specific goal.

Your original idea was:

> Use a powerful model (Qwen 3.6 27B) as an architect and a smaller model (Qwen 3.5 9B) as the implementation worker.

After expanding the architecture into twenty chapters, that idea still holds up remarkably well. The key improvement is that the "planner" should **not** decompose tasks all the way down to individual edits. Instead, it should produce coherent implementation tasks (for example, "Implement JWT authentication in the backend" rather than "Add line X to file Y"). The Worker, equipped with the Context Engine and Tool Engine, should retain enough autonomy to decide which files to inspect and modify.

This balance keeps the expensive reasoning model focused on strategic decisions while allowing the faster coding model to work efficiently in short-lived contexts.

If you build AI Loom in the order described throughout this specification, you'll end up with a system that is both practical on your hardware today and capable of growing into a much more powerful engineering platform over time.

---

**End of Chapter 20 — End of AI Loom Architecture Specification v1.0**
