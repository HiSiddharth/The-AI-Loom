# AI Loom Architecture Specification

# Chapter 12 — Memory System & Knowledge Management

**Version:** 1.0 Draft

---

# 12.1 Purpose

The Memory System allows AI Loom to work on projects for hours, days or even weeks without losing important context.

Unlike a chatbot, AI Loom does **not** rely on conversation history.

Instead, it maintains structured memories that evolve independently of the LLM context window.

The Memory System answers:

> **"What should the system remember, and what should it forget?"**

---

# 12.2 Design Philosophy

Memory should be:

* Structured
* Persistent
* Searchable
* Explainable
* Incrementally updated
* Independent of any model

Memory is **not** a transcript.

It is distilled knowledge.

---

# 12.3 Memory Layers

AI Loom maintains five independent memory layers.

```text
                    Memory
                       │
      ┌────────────────┼────────────────┐
      ▼                ▼                ▼
Project Memory   Session Memory   Task Memory
      │
      ▼
Architectural Memory

      ▼
User Preference Memory
```

Each layer has different lifetimes and update rules.

---

# 12.4 Project Memory

Project Memory represents long-lived knowledge about a repository.

Examples:

```text
Architecture

Frameworks

Folder Structure

Coding Style

Common Patterns

Design Decisions

Known Limitations
```

Persists until the repository changes significantly.

---

# 12.5 Session Memory

Lives for a single execution session.

Stores:

```text
Completed Tasks

Planner Decisions

Current Goal

Open Questions

Temporary Constraints
```

Destroyed when the session ends unless checkpointed.

---

# 12.6 Task Memory

Lives only during execution of one task.

Contains:

```text
Files Read

Assumptions

Intermediate Results

Tool Outputs

Failures

Observations
```

Destroyed after task completion.

---

# 12.7 Architectural Memory

Stores decisions that influence future work.

Examples:

```text
Repository uses Repository Pattern.

Authentication uses JWT.

Always use dependency injection.

API follows REST conventions.

Database migrations handled with Alembic.
```

Planner consults this before creating new tasks.

---

# 12.8 User Preference Memory

Optional.

Examples:

```text
Prefer minimal dependencies.

Avoid Docker.

Use TypeScript.

Follow Clean Architecture.

Prefer async APIs.
```

Applies across sessions.

Stored separately from repository knowledge.

---

# 12.9 Memory Objects

Every memory entry follows:

```text
MemoryEntry

ID

Category

Title

Content

Importance

Confidence

Created

Updated

Source

Version

Tags
```

---

# 12.10 Importance Levels

```text
LOW

NORMAL

HIGH

CRITICAL
```

Importance influences retention.

---

# 12.11 Confidence Levels

```text
0–100
```

Examples:

```text
Observed directly

100

Planner inference

70

Worker assumption

40
```

Low-confidence memories may expire sooner.

---

# 12.12 Sources

Every memory records where it came from.

Examples:

```text
Planner

Worker

Indexer

User

Git History

Configuration

Inference
```

Nothing enters memory anonymously.

---

# 12.13 Memory Lifecycle

```text
Create

↓

Validate

↓

Store

↓

Retrieve

↓

Update

↓

Archive

↓

Delete
```

Every transition is logged.

---

# 12.14 Memory Categories

Project:

```text
Architecture

Framework

Dependency

Folder Structure
```

Session:

```text
Decision

Constraint

Objective

Progress
```

Task:

```text
Observation

Tool Output

Failure

Patch
```

---

# 12.15 Memory Creation Rules

Only important information should be stored.

Good:

```text
Project uses SQLAlchemy.
```

Bad:

```text
Worker opened auth.py.
```

Transient events belong in logs.

---

# 12.16 Retrieval

Retrieval pipeline:

```text
Current Task

↓

Determine Memory Types

↓

Rank Memories

↓

Apply Budget

↓

Return
```

Workers never receive every memory.

---

# 12.17 Ranking

Ranking factors:

| Signal          | Weight |
| --------------- | -----: |
| Same Task Type  |    100 |
| Same Symbols    |     90 |
| Same Files      |     80 |
| High Importance |     70 |
| Recent          |     60 |
| High Confidence |     50 |

Only top-ranked memories are retrieved.

---

# 12.18 Memory Budget

Memory competes with source code for context.

Suggested allocation:

| Section   | Budget |
| --------- | -----: |
| Objective |     5% |
| Memory    |    15% |
| Code      |    60% |
| Summaries |    15% |
| Tools     |     5% |

Memory should never dominate prompts.

---

# 12.19 Updating Memory

When new information arrives:

```text
Existing Entry

↓

Conflict?

↓

Merge

↓

Update Version
```

Avoid duplicates.

---

# 12.20 Conflict Resolution

Example:

Old:

```text
Uses Flask.
```

New:

```text
Migrated to FastAPI.
```

Result:

```text
Old → Archived

New → Active
```

Nothing is silently overwritten.

---

# 12.21 Forgetting

Not all memories are permanent.

Candidates for removal:

* Expired temporary constraints
* Failed assumptions
* Old session progress
* Obsolete architectural decisions

---

# 12.22 Checkpoint Memory

Each checkpoint stores:

```text
Session Memory

Planner State

Task Graph

Current Worker

Progress
```

Allows exact resumption.

---

# 12.23 Memory Queries

Public API:

```text
find_by_tag()

find_by_category()

find_recent()

find_related()

find_project()

find_session()

find_task()
```

Planner and Worker never access storage directly.

---

# 12.24 Architectural Decisions

Major architectural choices become first-class objects.

Example:

```text
Decision

Authentication

JWT

Reason

Already integrated with frontend

Status

Accepted
```

Future tasks reference these instead of rediscovering them.

---

# 12.25 Lessons Learned

After difficult tasks:

```text
Issue

Root Cause

Resolution

Applies To

Confidence
```

Example:

```text
FastAPI project requires lifespan startup.

Confidence

100
```

This improves future planning.

---

# 12.26 Anti-Memories

Not every observation should become future knowledge.

Example:

```text
Attempted Approach

Failed

Reason

Import cycle
```

Future planners avoid repeating known failures.

---

# 12.27 Memory Compression

Large memories are periodically summarised.

Example:

```text
20 Decisions

↓

Summary

↓

Archive Originals
```

Raw entries remain recoverable if needed.

---

# 12.28 Semantic Search

Memory retrieval supports:

* Tags
* Categories
* Symbol references
* Semantic similarity (optional)

Structural queries remain the primary method.

---

# 12.29 Versioning

Every update creates a new version.

```text
v1

↓

v2

↓

v3
```

Previous versions remain accessible for debugging.

---

# 12.30 Storage

Suggested storage:

```text
SQLite

Tables

memory_entries

memory_links

memory_versions

memory_tags

architectural_decisions

lessons
```

No dependency on vector databases.

---

# 12.31 Performance Targets

Target latency:

| Operation      |  Target |
| -------------- | ------: |
| Insert         | < 10 ms |
| Retrieve       | < 20 ms |
| Update         | < 15 ms |
| Version Lookup | < 30 ms |

Memory access should be negligible compared to model inference.

---

# 12.32 Design Constraints

1. Memory stores knowledge, not conversations.
2. Every entry has a source and confidence.
3. Session memory is isolated between sessions.
4. Project memory survives restarts.
5. Memory retrieval is deterministic.
6. Memory updates are versioned.
7. Memory never exceeds its configured context budget.
8. Failed assumptions must not become permanent knowledge.
9. Planner and Worker consume memory through APIs only.
10. Memory is explainable—every retrieved item must justify why it was selected.

---

# Architect's Notes (Normative)

## 1. Separate Memory from Logs

A common mistake is treating logs as memory.

Example:

**Log**

```text
Read auth.py
Ran pytest
Patched login()
```

**Memory**

```text
Authentication uses JWT with rotating refresh tokens.
```

Logs describe events.

Memory describes knowledge.

---

## 2. Memory Should Be Explicitly Linked

Memory entries should reference related entities.

Example:

```text
Memory

↓

Symbol:
AuthService.login()

↓

File:
src/auth.py

↓

Decision:
Use JWT
```

This enables graph-based retrieval rather than keyword search.

---

## 3. Introduce Reflection (Future)

After major milestones, optionally invoke a lightweight reflection model.

Example:

```text
Completed Feature

↓

Reflection

↓

Lessons Learned

↓

Architectural Memory
```

This converts repeated experience into reusable knowledge without polluting task execution.

---

## 4. Never Trust Model Inference Blindly

Only persist inferred knowledge after verification.

For example:

* "Project appears to use Repository Pattern" → tentative (confidence 60)
* After structural confirmation by the indexer → confirmed (confidence 100)

The Memory System should distinguish facts from hypotheses.

---

## 5. Keep Memory Model-Agnostic

Memory must never contain model-specific artefacts such as prompts, chain-of-thought or provider metadata.

It should remain valid regardless of whether AI Loom uses Qwen, DeepSeek, Gemini or another future model.

The Memory System is a long-lived knowledge layer, not an extension of any single LLM.

---