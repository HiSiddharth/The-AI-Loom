# AI Loom Architecture Specification

# Chapter 3 — Repository Structure & Module Organization

**Version:** 1.0 Draft

---

# 3.1 Purpose

This chapter defines the complete repository layout of AI Loom.

The objectives are:

* Every file has one responsibility.
* Every module has a clear public interface.
* Circular dependencies are impossible.
* Infrastructure can be replaced without affecting orchestration.
* New tools, models, or planners can be added with minimal changes.

This structure is mandatory for Version 1.

---

# 3.2 Repository Layout

```text
ai-loom/

├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.lock
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Dockerfile
│
├── docs/
│
├── configs/
│
├── prompts/
│
├── scripts/
│
├── tests/
│
├── examples/
│
├── migrations/
│
└── src/
```

Only `src/` contains production code.

---

# 3.3 Source Layout

```text
src/

├── api/
├── core/
├── graph/
├── planner/
├── workers/
├── tools/
├── models/
├── indexing/
├── memory/
├── sessions/
├── events/
├── storage/
├── infrastructure/
├── permissions/
├── prompts/
├── telemetry/
├── utils/
└── main.py
```

---

# 3.4 Top-Level Responsibilities

| Folder         | Responsibility       |
| -------------- | -------------------- |
| api            | HTTP server          |
| core           | Shared domain models |
| graph          | LangGraph workflow   |
| planner        | Planning engine      |
| workers        | Coding workers       |
| tools          | Tool system          |
| models         | Model routing        |
| indexing       | Code intelligence    |
| memory         | Context builder      |
| sessions       | Session lifecycle    |
| events         | Event bus            |
| storage        | Database layer       |
| infrastructure | External systems     |
| permissions    | Security             |
| prompts        | Prompt templates     |
| telemetry      | Logs & metrics       |
| utils          | Shared helpers       |

---

# 3.5 API Module

```text
api/

├── server.py
├── routes.py
├── middleware.py
├── streaming.py
├── serializers.py
├── validators.py
├── dependencies.py
└── schemas.py
```

Responsibilities:

* OpenAI-compatible endpoints
* Streaming
* Authentication (future)
* Request validation

Forbidden:

* Planning
* Tool execution
* Model selection

---

# 3.6 Core Module

Contains domain objects.

```text
core/

├── task.py
├── session.py
├── worker.py
├── workspace.py
├── models.py
├── enums.py
├── exceptions.py
└── constants.py
```

Contains only:

* dataclasses
* enums
* interfaces
* shared constants

No business logic.

---

# 3.7 Graph Module

Owns LangGraph.

```text
graph/

├── graph.py
├── state.py
├── nodes/
├── edges/
├── transitions.py
├── checkpoints.py
└── executor.py
```

---

Nodes:

```text
nodes/

planner.py

scheduler.py

worker.py

review.py

tool.py

retry.py

approval.py

finish.py
```

Every node performs exactly one operation.

---

# 3.8 Planner Module

```text
planner/

├── planner.py
├── decomposition.py
├── dependency_graph.py
├── estimator.py
├── verifier.py
├── reviewer.py
├── strategies.py
└── prompts.py
```

Responsibilities:

* break work
* prioritize
* estimate
* review

Never edits files.

---

# 3.9 Workers Module

```text
workers/

├── worker.py
├── coding.py
├── debugging.py
├── refactoring.py
├── documentation.py
├── testing.py
└── prompts.py
```

Version 1 only instantiates one generic coding worker.

The specialized workers share infrastructure.

---

# 3.10 Tools Module

```text
tools/

├── registry.py
├── executor.py
├── validation.py
├── results.py
│
├── filesystem/
├── terminal/
├── git/
├── search/
├── packages/
├── browser/
└── workspace/
```

Every tool category lives independently.

---

Filesystem:

```text
filesystem/

read.py

write.py

move.py

copy.py

delete.py

mkdir.py

tree.py
```

---

Terminal:

```text
terminal/

run.py

cancel.py

sandbox.py

parser.py
```

---

Git:

```text
git/

status.py

diff.py

commit.py

restore.py

branch.py
```

---

# 3.11 Model Module

```text
models/

├── router.py
├── loader.py
├── registry.py
├── provider.py
├── lmstudio.py
├── tokenizer.py
├── cache.py
├── health.py
└── prompts.py
```

Responsibilities:

* load models
* unload models
* route requests
* health checks

No planning logic.

---

# 3.12 Indexing Module

```text
indexing/

├── scanner.py
├── parser.py
├── symbols.py
├── references.py
├── summaries.py
├── embeddings.py
├── dependency.py
├── incremental.py
├── watcher.py
└── queries.py
```

Subfolders:

```text
languages/

python.py

typescript.py

cpp.py

java.py

rust.py
```

Each language adapter wraps Tree-sitter.

---

# 3.13 Memory Module

```text
memory/

context_builder.py

compression.py

retrieval.py

ranking.py

summaries.py

history.py
```

Responsibilities:

Build worker prompts.

---

# 3.14 Session Module

```text
sessions/

manager.py

workspace.py

resume.py

snapshot.py

cleanup.py

locks.py
```

Every conversation owns one Session object.

---

# 3.15 Event Module

```text
events/

bus.py

publisher.py

subscriber.py

logger.py

types.py

handlers.py
```

Every subsystem communicates through events.

No direct callbacks.

---

# 3.16 Storage Module

```text
storage/

database.py

repositories/

migrations/

models/

sqlite.py
```

Repositories:

```text
repositories/

symbols.py

tasks.py

sessions.py

summaries.py

embeddings.py

logs.py
```

---

# 3.17 Infrastructure Module

```text
infrastructure/

filesystem.py

terminal.py

lmstudio.py

git.py

watcher.py

process.py

clock.py
```

Contains wrappers over external systems.

Never imports planner.

---

# 3.18 Permissions Module

```text
permissions/

policy.py

approval.py

workspace.py

filesystem.py

terminal.py
```

Owns security decisions.

---

# 3.19 Prompt Module

```text
prompts/

planner/

worker/

reviewer/

system/

compression/
```

Each prompt stored as Markdown.

Example:

```text
planner/

system.md

planning.md

verification.md
```

No prompt strings inside Python files.

---

# 3.20 Telemetry

```text
telemetry/

logger.py

metrics.py

events.py

timing.py

tracing.py
```

Supports future OpenTelemetry integration.

---

# 3.21 Utils

Contains only generic helpers.

```text
utils/

hashing.py

json.py

paths.py

strings.py

async.py
```

Never contains business logic.

---

# 3.22 Tests

```text
tests/

unit/

integration/

e2e/

fixtures/

workspaces/
```

Every module has matching tests.

---

# 3.23 Prompt Assets

Repository root:

```text
prompts/

planner.md

worker.md

reviewer.md

compression.md

summarizer.md

debugger.md
```

These are editable without changing code.

---

# 3.24 Configuration

```text
configs/

default.yaml

models.yaml

permissions.yaml

logging.yaml

indexing.yaml
```

Every subsystem owns one config file.

---

# 3.25 Documentation

```text
docs/

architecture/

api/

prompts/

design/

examples/
```

Architecture chapters live here.

---

# 3.26 Scripts

```text
scripts/

bootstrap.py

reindex.py

benchmark.py

export_db.py

clean.py
```

Scripts never contain reusable business logic.

---

# 3.27 Examples

```text
examples/

python/

react/

fastapi/

cpp/
```

Used for testing and benchmarking.

---

# 3.28 Dependency Rules

Allowed:

```text
API

↓

Graph

↓

Planner

↓

Workers

↓

Tools

↓

Infrastructure
```

Forbidden:

Infrastructure → Planner

Workers → API

Indexing → Planner

Storage → Graph

Graph → SQLite

Every dependency must point downward.

---

# 3.29 Public Interfaces

Each package exports a single entry point.

Example:

```python
class PlannerService:
    ...
```

Internal implementation remains private.

Other packages never import implementation classes directly.

---

# 3.30 Module Ownership

Every module owns exactly one concern.

Examples:

Planner

* Plans

Worker

* Writes code

Router

* Chooses model

Executor

* Executes tools

Parser

* Parses AST

Scanner

* Finds files

Watcher

* Watches filesystem

This rule is absolute.

---

# 3.31 Future Extensions

The repository layout intentionally leaves room for:

```text
plugins/

providers/

mcp/

distributed/

web/

ide/
```

These can be added without restructuring existing modules.

---

# 3.32 Repository Principles

1. One responsibility per module.
2. One public interface per package.
3. No circular imports.
4. Infrastructure is replaceable.
5. Prompts are data, not code.
6. Business logic never lives in API handlers.
7. Domain models are independent of frameworks.
8. External systems are wrapped behind adapters.
9. All filesystem access goes through the Tool layer.
10. Every package is independently testable.

---

# 3.33 Repository Tree (Simplified)

```text
ai-loom/
│
├── docs/
├── prompts/
├── configs/
├── tests/
├── scripts/
└── src/
    ├── api/
    ├── core/
    ├── graph/
    ├── planner/
    ├── workers/
    ├── models/
    ├── tools/
    ├── indexing/
    ├── memory/
    ├── sessions/
    ├── events/
    ├── storage/
    ├── permissions/
    ├── infrastructure/
    ├── telemetry/
    └── main.py
```

---