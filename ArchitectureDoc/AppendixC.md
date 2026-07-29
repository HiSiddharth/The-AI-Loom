# AI Loom Architecture Specification

# Appendix C — AI Loom MVP (v0.1) Implementation Blueprint

**Version:** 1.0 Draft

---

# C.1 Purpose

This appendix intentionally **deviates from the full architecture**.

The previous chapters describe the *ideal* AI Loom.

This appendix describes **the version you should actually build first.**

The goal is to produce a system that is:

* Useful
* Fast
* Stable
* Small enough for one developer
* Optimised for your RTX 4060 (8 GB VRAM)

This is the shortest path to something you can use every day.

---

# C.2 Guiding Principle

Don't build an AI Operating System first.

Build the **best local coding agent** you can.

Every feature in the MVP should justify its complexity.

---

# C.3 MVP Architecture

```text
                   User

                     │

                     ▼

                OpenCode UI

                     │

                     ▼

              AI Loom Backend

                     │

     ┌───────────────┼────────────────┐

     ▼               ▼                ▼

 Planner       Context Engine     Tool Engine

     │               │

     ▼               ▼

 Repository Index     Memory

     │

     ▼

 Worker

     │

     ▼

 Validation

     │

     ▼

 Response
```

Notice what is **missing**:

* Multiple Workers
* Distributed execution
* Plugin marketplace
* Remote execution
* Workflow engine
* Multiple planners

---

# C.4 Primary Workflow

```text
User Goal

↓

Planner (27B)

↓

Task List

↓

Worker (9B)

↓

Tools

↓

Validation

↓

Planner Review

↓

Return Result
```

This should be the only workflow implemented initially.

---

# C.5 Planner Model

Recommended:

**Qwen 3.6 27B**

Responsibilities:

* Understand objective
* Break into tasks
* Decide validation
* Review results
* Decide retries

The planner should **never** edit files directly.

---

# C.6 Worker Model

Recommended:

**Qwen 3.5 9B**

Responsibilities:

* Read files
* Search code
* Call tools
* Edit files
* Fix validation failures

Every task gets a **fresh context**.

This is one of the biggest advantages of your design.

---

# C.7 Model Lifecycle

Instead of loading both models permanently:

```text
Planner Needed

↓

Load 27B

↓

Plan

↓

Unload

↓

Load 9B

↓

Execute

↓

Unload

↓

Load 27B

↓

Review

↓

Done
```

This conserves VRAM and aligns with your existing model-loading strategy.

---

# C.8 Context Window Strategy

Planner:

* 16k context
* High-quality summaries
* Project overview
* Task history

Worker:

* 32k–64k context (if feasible)
* Only relevant files
* Fresh session per task

Never keep long-running Worker conversations.

---

# C.9 Repository Index

The MVP index stores:

* File list
* Symbols
* Imports
* Definitions
* References
* Dependency graph

Do **not** implement embeddings initially.

Tree-sitter is sufficient.

---

# C.10 Context Retrieval

Retrieval order:

```text
Requested Symbol

↓

Definition

↓

Dependencies

↓

Callers

↓

Related Files

↓

Documentation
```

Avoid semantic search unless structural search fails.

---

# C.11 Memory

Implement only three memory types:

### Session Memory

Current task.

Deleted when session ends.

---

### Project Memory

Stored in SQLite.

Contains:

* Framework
* Build commands
* Test commands
* Coding conventions

---

### Architecture Memory

Stores decisions like:

```text
Authentication uses JWT.

Database uses SQLAlchemy.

API routes live under /api.
```

No conversational memory yet.

---

# C.12 Tool Set

Version 0.1 should include only:

```text
Read File

Write File

Search

List Directory

Run Command

Git Diff
```

Nothing more.

Every additional tool increases testing complexity.

---

# C.13 Permission Model

Simple policy:

| Tool    | Default        |
| ------- | -------------- |
| Read    | Allow          |
| Search  | Allow          |
| List    | Allow          |
| Write   | Ask once       |
| Command | Ask every time |

This is sufficient for an MVP.

---

# C.14 Validation

Only implement:

* Build
* Lint
* Unit tests

Reviewer model comes later if needed.

---

# C.15 Event System

Keep it simple.

Events:

```text
Task Started

Task Finished

Tool Called

Validation Started

Validation Finished

Error
```

No advanced tracing yet.

---

# C.16 Configuration

Single YAML file:

```yaml
planner:
  profile: planner

worker:
  profile: worker

permissions:
  write: ask
  command: ask

validation:
  lint: true
  tests: affected
```

No profile inheritance.

No runtime reloading.

---

# C.17 Storage

SQLite database.

Tables:

```text
projects

sessions

memory

tasks

events
```

Nothing more.

---

# C.18 CLI Commands

Implement only:

```bash
ailoom run

ailoom index

ailoom doctor

ailoom config
```

Additional commands can wait.

---

# C.19 Success Criteria

The MVP succeeds if it can reliably complete prompts like:

* "Add JWT authentication."
* "Fix this failing test."
* "Refactor this module."
* "Implement dark mode."
* "Create a FastAPI CRUD API."
* "Generate documentation for this package."

without requiring manual file navigation.

---

# C.20 Explicit Non-Goals

Do **not** build these in v0.1:

* Parallel Workers
* Plugin marketplace
* Distributed execution
* Embeddings database
* Autonomous background tasks
* Automatic package installation
* Browser automation
* Voice interface
* GUI

Each adds substantial complexity without improving the core coding experience.

---

# C.21 Development Order

Build in this exact order:

```text
1. Runtime
2. Tool Engine
3. LM Studio Provider
4. Worker
5. Indexer
6. Context Engine
7. Planner
8. Validation
9. Memory
10. OpenCode Integration
```

Do not skip ahead.

---

# C.22 Definition of Done

The MVP is complete when you can:

1. Open any repository in OpenCode.
2. Ask AI Loom to implement a feature.
3. Watch it inspect only relevant files.
4. Generate a plan.
5. Execute edits.
6. Run validation.
7. Automatically fix failures if possible.
8. Present a final summary with the diff.

If this works consistently, you have a genuinely useful local coding agent.

---

# Architect's Final Recommendation

After reviewing your hardware, goals and the full architecture, this is the implementation I'd personally pursue:

* **Planner:** Qwen 3.6 27B (high reasoning, loaded only when needed)
* **Worker:** Qwen 3.5 9B (fast implementation with fresh contexts)
* **Provider:** LM Studio using the OpenAI-compatible API
* **Indexer:** Tree-sitter with incremental updates
* **Storage:** SQLite
* **Framework:** Pure Python with `asyncio`
* **UI:** OpenCode
* **Validation:** Native project tooling (`pytest`, `ruff`, `eslint`, etc.)
* **Communication:** Internal typed Python interfaces first; evolve toward ALP later

Most importantly, **avoid over-engineering the MVP**. The architecture you've designed can support a much larger system, but the fastest path to something valuable is a lean implementation focused on planning, context retrieval, execution and validation.

Once that foundation is reliable, nearly every advanced feature in the preceding chapters can be added incrementally without changing the core architecture.

---

**End of Appendix C**
