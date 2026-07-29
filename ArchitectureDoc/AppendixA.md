# AI Loom Architecture Specification

# Appendix A — Engineering Decisions & Recommended Technologies (Normative)

**Version:** 1.0 Draft

---

# A.1 Purpose

This appendix records the engineering decisions behind AI Loom.

Unlike the architecture chapters, this document answers:

> **"Why was this technology chosen?"**

These decisions are recommendations for the reference implementation and may be revised in future versions.

---

# A.2 Primary Language

## Decision

Python 3.12+

## Why

Python has:

* Excellent AI ecosystem
* Mature async support
* Tree-sitter bindings
* Pydantic
* Rich CLI libraries
* Large developer community

Most modern LLM tooling already targets Python.

---

# A.3 Async Runtime

## Decision

asyncio

Avoid threads unless unavoidable.

---

## Why

AI Loom spends most of its time:

* waiting for models
* reading files
* running subprocesses
* querying SQLite

These are I/O bound.

Async greatly simplifies orchestration.

---

# A.4 Data Validation

## Decision

Pydantic v2

Every message, configuration object and internal protocol object should be validated.

---

## Why

Benefits:

* Runtime validation
* IDE autocomplete
* JSON schema generation
* Type safety
* Serialization

---

# A.5 CLI Framework

## Decision

Typer

---

## Why

Advantages:

* Excellent type hints
* Easy subcommands
* Automatic help
* Mature ecosystem

Example:

```bash
ailoom index

ailoom run

ailoom review

ailoom config

ailoom doctor
```

---

# A.6 Configuration

## Decision

YAML

---

## Why

Readable.

Supports comments.

Supports nested configuration.

Widely understood.

---

# A.7 Internal Models

Every major object should have its own Pydantic model.

Examples:

```text
Task

WorkerState

PlannerState

Context

InferenceRequest

ValidationResult

Event

MemoryEntry

PermissionRequest
```

Avoid dictionaries.

---

# A.8 Storage

## Decision

SQLite

---

## Why

Stores:

* Memory
* Events
* Metadata
* Sessions
* Index metadata

Advantages:

* No server
* ACID
* Fast
* Portable

---

# A.9 Repository Index

## Decision

Tree-sitter

---

## Why

Tree-sitter provides:

* AST
* Incremental parsing
* Fast updates
* Multi-language support

This is the backbone of AI Loom.

---

# A.10 Search Engine

Use two layers.

Layer 1

Structural Search

```text
Symbols

Imports

References

Definitions
```

Layer 2

Semantic Search

(Optional)

```text
Embeddings
```

Structural search should always be attempted first.

---

# A.11 Embeddings

Version 1

Optional.

Do not make embeddings mandatory.

---

Reason

Symbol retrieval is significantly cheaper and often more accurate for code.

Embeddings are a complement, not a replacement.

---

# A.12 Model Communication

Decision

OpenAI-compatible API.

---

Why

Supports:

* LM Studio
* vLLM
* llama.cpp
* Many hosted providers

One adapter serves multiple providers.

---

# A.13 Provider Interface

Every provider implements:

```python
chat()

stream()

models()

health()

embeddings()
```

No provider-specific logic outside adapters.

---

# A.14 Event System

Decision

Internal asynchronous event bus.

Avoid direct logging from business logic.

---

Benefits

* UI
* Metrics
* Plugins
* Dashboard

all consume the same events.

---

# A.15 Logging

Structured logging.

Example:

```json
{
  "worker":"worker_2",
  "task":"task_31",
  "duration":5.1
}
```

Avoid free-form strings.

---

# A.16 Testing

Decision

pytest

Mandatory:

* Unit tests
* Integration tests

Optional:

* Property tests
* Benchmarks

---

# A.17 Dependency Injection

Decision

Constructor injection.

Avoid service locators where possible.

---

Good

```python
Planner(
    router,
    context,
    memory
)
```

Bad

```python
Global.router
```

---

# A.18 Concurrency

Decision

Async tasks.

Avoid thread pools.

Use subprocesses for:

* terminal
* git
* tests

---

# A.19 Git Operations

Never implement Git manually.

Always invoke Git itself.

Example

```bash
git status

git diff

git apply
```

Git is already the source of truth.

---

# A.20 Patching

Decision

Unified diff patches.

Worker outputs:

```diff
+ new code

- old code
```

Tool Engine applies.

Never allow direct string replacement.

---

# A.21 File Watching

Recommended

watchfiles

or

watchdog

Purpose

Incremental indexing.

---

# A.22 Validation

Use native project tooling.

Python

```text
pytest

ruff

black
```

Node

```text
eslint

vitest

prettier
```

Rust

```text
cargo test
```

Never reinvent validators.

---

# A.23 Prompt Templates

Store prompts separately.

```text
prompts/

planner.md

worker.md

reviewer.md
```

Never hardcode prompts inside Python.

---

# A.24 Context Assembly

Separate module.

Responsibilities

* token estimation
* ordering
* truncation
* compression

Planner never assembles prompts.

---

# A.25 Serialization

Version 1

JSON

Future

Protocol Buffers

if distributed execution becomes common.

---

# A.26 Plugin Loading

Use Python entry points later.

Initially

Filesystem discovery is sufficient.

---

# A.27 API

Future

FastAPI

Reason

Easy async integration.

Automatic OpenAPI.

---

# A.28 Frontend

Do not build one initially.

CLI first.

API second.

Web UI later.

---

# A.29 Package Management

Dependency manager

uv

Reasons:

* Extremely fast
* Lockfiles
* Modern Python workflows

---

# A.30 Project Structure

Recommended

```text
ailoom/

core/

planner/

worker/

routing/

context/

memory/

events/

indexer/

tools/

validation/

runtime/

providers/

plugins/

api/

cli/

config/

tests/

docs/
```

---

# A.31 Code Style

Mandatory

* Type hints everywhere
* Small functions
* Pure functions where possible
* Immutable models where practical

Avoid clever abstractions.

---

# A.32 Performance Targets

Index lookup

<10 ms

Context assembly

<50 ms

Permission check

<1 ms

Task creation

<20 ms

SQLite query

<5 ms

---

# A.33 Documentation

Maintain:

Architecture

API

Plugin Guide

Developer Guide

Configuration

No undocumented public APIs.

---

# A.34 Security

Never trust:

* model outputs
* filesystem paths
* plugins
* shell arguments

Validate everything.

---

# A.35 Final Recommendation

For your first implementation, keep the stack intentionally simple:

```text
Python 3.12

↓

uv

↓

Typer

↓

Pydantic

↓

asyncio

↓

SQLite

↓

Tree-sitter

↓

LM Studio

↓

Qwen 3.6 27B

↓

Qwen 3.5 9B

↓

OpenCode
```

Resist adding technologies simply because they're popular. Every additional dependency increases maintenance burden.

---

# Architect's Notes

After reviewing the entire specification, there are three architectural decisions I would make slightly differently if starting from scratch:

### 1. Replace LangGraph with a Lightweight Internal Workflow Engine

Originally, you planned to build around LangGraph. After defining the architecture, that no longer seems necessary.

Your planner, task queue, worker orchestration and event bus already form a domain-specific workflow engine. Building a thin internal orchestrator will likely be simpler, easier to debug and avoid unnecessary abstractions.

---

### 2. Make the Indexer the Centre of the System

Initially, it appears that the Planner is the "brain."

In practice, the Indexer becomes the most valuable component.

Every subsystem depends on it:

* Context Engine
* Planner
* Worker
* Validation
* Memory
* Reviewers

Invest heavily in making indexing fast, incremental and accurate. Improvements here will benefit every other component.

---

### 3. Keep the Planner Small

Avoid the temptation to let the Planner micromanage Workers.

The Planner should answer:

* What should be built?
* In what order?
* What constraints exist?

The Worker should answer:

* Which files?
* Which symbols?
* Which edits?
* Which tools?

This separation keeps your 27B model focused on strategic reasoning while allowing the 9B coding model to operate efficiently in fresh, bounded contexts—exactly the workflow your hardware is well suited to.

---

**End of Appendix A**
