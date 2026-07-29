# AI Loom Architecture Specification

# Appendix B — Repository Layout & File-by-File Specification (Normative)

**Version:** 1.0 Draft

---

# B.1 Purpose

This appendix defines the **physical structure** of the AI Loom repository.

While previous chapters described the architecture conceptually, this appendix specifies:

* Every major package
* Its responsibility
* Important files
* Public interfaces
* Dependencies
* Ownership boundaries

This serves as the blueprint for implementation.

---

# B.2 Top-Level Repository Layout

```text
ailoom/
│
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
│
├── docs/
├── tests/
├── scripts/
├── prompts/
├── configs/
├── plugins/
├── examples/
│
├── ailoom/
│   ├── api/
│   ├── cli/
│   ├── config/
│   ├── core/
│   ├── events/
│   ├── planner/
│   ├── workers/
│   ├── routing/
│   ├── providers/
│   ├── context/
│   ├── indexer/
│   ├── retrieval/
│   ├── memory/
│   ├── validation/
│   ├── permissions/
│   ├── tools/
│   ├── runtime/
│   ├── observability/
│   ├── plugins/
│   ├── storage/
│   └── utils/
│
└── main.py
```

---

# B.3 Root Files

## pyproject.toml

Contains:

* Dependencies
* Build configuration
* Tool configuration
* Entry points
* Version

---

## uv.lock

Dependency lockfile.

Never edit manually.

---

## README.md

Contains:

* Overview
* Installation
* Quick Start
* Examples

---

## LICENSE

Project licence.

---

## .env.example

Environment variables only.

Never store secrets.

---

# B.4 docs/

Contains all documentation.

```text
docs/

architecture/

developer-guide/

plugin-guide/

api/

tutorials/

benchmarks/
```

Documentation evolves with code.

---

# B.5 prompts/

Contains every LLM prompt.

Example:

```text
planner.md

worker.md

reviewer.md

context.md

summarizer.md
```

Prompt versioning happens independently from code.

---

# B.6 configs/

Default configurations.

Example:

```text
default.yaml

offline.yaml

performance.yaml

development.yaml
```

Users override these.

---

# B.7 scripts/

Utility scripts.

Examples:

```text
benchmark.py

generate_docs.py

profile_indexer.py

release.py
```

Scripts never contain application logic.

---

# B.8 examples/

Reference projects.

Example:

```text
python/

fastapi/

react/

node/

java/
```

Used for benchmarks and testing.

---

# B.9 tests/

Mirror production structure.

Example:

```text
tests/

planner/

workers/

context/

routing/

providers/

validation/

integration/

end_to_end/
```

Every package has corresponding tests.

---

# B.10 ailoom/core/

Purpose:

Shared domain models.

Contains:

```text
models.py

interfaces.py

exceptions.py

constants.py

types.py
```

No business logic.

Every package depends on Core.

Core depends on nothing.

---

# B.11 ailoom/config/

Responsible for:

* Loading YAML
* Environment overrides
* Validation
* Profiles

Files:

```text
loader.py

models.py

profiles.py

defaults.py
```

---

# B.12 ailoom/events/

Implements Event Bus.

Files:

```text
bus.py

events.py

publisher.py

subscriber.py
```

Every component publishes events.

---

# B.13 ailoom/runtime/

Owns lifecycle.

Files:

```text
runtime.py

services.py

startup.py

shutdown.py

health.py
```

Coordinates the application.

---

# B.14 ailoom/providers/

Contains provider adapters.

Example:

```text
base.py

lmstudio.py

ollama.py

openai.py
```

Only provider-specific code belongs here.

---

# B.15 ailoom/routing/

Responsible for model selection.

Files:

```text
router.py

profiles.py

policies.py

costs.py
```

Planner never selects models directly.

---

# B.16 ailoom/planner/

Contains:

```text
planner.py

task_graph.py

scheduler.py

review.py

constraints.py
```

Produces task graphs.

---

# B.17 ailoom/workers/

Contains:

```text
worker.py

executor.py

state.py

prompts.py

results.py
```

One Worker = one implementation task.

---

# B.18 ailoom/tools/

Contains:

```text
dispatcher.py

filesystem.py

terminal.py

git.py

search.py
```

Every tool is isolated.

---

# B.19 ailoom/context/

Responsible for prompt assembly.

Files:

```text
assembler.py

budget.py

compressor.py

ranking.py
```

Consumes retrieval results.

---

# B.20 ailoom/retrieval/

Responsible for finding relevant code.

Files:

```text
retriever.py

symbol_search.py

embedding_search.py

dependency_search.py
```

Produces ranked context.

---

# B.21 ailoom/indexer/

Contains:

```text
indexer.py

watcher.py

treesitter.py

graph.py

cache.py
```

Owns repository understanding.

---

# B.22 ailoom/memory/

Contains:

```text
session.py

project.py

architecture.py

storage.py
```

Different memory types remain separate.

---

# B.23 ailoom/storage/

Responsible for persistence.

Files:

```text
sqlite.py

schema.py

migrations.py
```

Only persistence logic belongs here.

---

# B.24 ailoom/permissions/

Contains:

```text
manager.py

policies.py

sandbox.py

audit.py
```

All privileged operations pass here.

---

# B.25 ailoom/validation/

Contains:

```text
pipeline.py

validators.py

results.py

profiles.py
```

Coordinates validators.

---

# B.26 ailoom/observability/

Contains:

```text
metrics.py

timeline.py

tracing.py

dashboard.py
```

Nothing here affects business logic.

---

# B.27 ailoom/plugins/

Responsible for:

* Discovery
* Loading
* Registration

Files:

```text
loader.py

registry.py

manifest.py

manager.py
```

---

# B.28 ailoom/api/

Future REST interface.

Files:

```text
server.py

routes.py

models.py
```

Optional in v1.

---

# B.29 ailoom/cli/

CLI implementation.

Example:

```text
main.py

run.py

index.py

doctor.py

config.py
```

Thin wrapper around Runtime.

---

# B.30 ailoom/utils/

Shared helpers only.

Examples:

```text
tokens.py

hashing.py

timing.py

filesystem.py
```

Avoid business logic here.

---

# B.31 Dependency Rules

Allowed:

```text
CLI

↓

Runtime

↓

Planner

↓

Worker

↓

Context

↓

Retrieval

↓

Indexer

↓

Storage
```

Forbidden:

Indexer importing Planner.

Worker importing CLI.

Provider importing Runtime.

---

# B.32 Import Policy

Imports should always point downward.

Never create circular dependencies.

If two packages depend on each other:

Move shared code into Core.

---

# B.33 Public APIs

Every package exposes a small public interface.

Example:

```python
planner/

__init__.py

↓

Planner
```

Internal modules remain private.

---

# B.34 Naming Conventions

Classes:

```text
PascalCase
```

Functions:

```text
snake_case
```

Constants:

```text
UPPER_CASE
```

Files:

```text
snake_case.py
```

---

# B.35 Ownership

Each package should have a clearly defined owner.

Example:

| Package    | Responsibility           |
| ---------- | ------------------------ |
| Planner    | Task decomposition       |
| Worker     | Code generation          |
| Context    | Prompt assembly          |
| Indexer    | Repository understanding |
| Validation | Code verification        |
| Routing    | Model selection          |

No overlapping responsibilities.

---

# B.36 Design Constraints

1. Every package has one responsibility.
2. Dependencies always flow downward.
3. Core has no dependencies.
4. Business logic never lives in utilities.
5. Runtime owns lifecycle.
6. CLI remains thin.
7. Storage is isolated.
8. Plugins remain optional.
9. Public APIs stay small.
10. Repository structure reflects architecture.

---

# Architect's Notes

## 1. Treat Packages Like Independent Products

Each package should be understandable in isolation.

A contributor working on the Indexer should rarely need to understand the Planner internals.

Strong boundaries improve maintainability.

---

## 2. Resist the "utils.py" Trap

Large utility modules often become dumping grounds.

If a helper starts acquiring business logic, promote it into a proper package with a clear responsibility.

---

## 3. Keep the Dependency Graph Acyclic

One of the easiest ways to preserve architectural quality is to regularly generate and inspect the package dependency graph.

Any cycle is a design smell.

---

## 4. Minimise Public Surface Area

Only expose the interfaces other packages genuinely need.

Everything else should remain internal implementation details.

This gives you the freedom to refactor aggressively without breaking other parts of the system.

---

## 5. Let the Repository Tell the Story

A new contributor should be able to glance at the directory structure and immediately infer:

* where planning happens,
* where indexing happens,
* where model routing happens,
* where validation happens,
* and where runtime orchestration lives.

If the folder layout communicates the architecture, the codebase becomes much easier to navigate and evolve.

---

**End of Appendix B**
