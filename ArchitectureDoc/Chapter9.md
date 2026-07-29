# AI Loom Architecture Specification

# Chapter 9 — Worker Engine

**Version:** 1.0 Draft

---

# 9.1 Purpose

The Worker Engine is responsible for executing exactly **one task**.

A worker is **not** an autonomous agent.

It is a deterministic execution engine whose job is to transform a well-defined objective into verified code changes using tools.

The Worker does not:

* plan
* reprioritise tasks
* decompose work
* decide architecture

Those belong to the Planner.

---

# 9.2 Philosophy

The worker follows a simple principle:

> **Observe → Think → Act → Verify → Repeat**

Never:

> Think forever.

Every reasoning cycle should result in either:

* a tool call
* task completion
* clarification request
* failure

---

# 9.3 Responsibilities

The Worker is responsible for:

* Understanding one task
* Reading relevant code
* Writing code
* Calling tools
* Responding to tool outputs
* Detecting errors
* Completing the assigned objective

Nothing more.

---

# 9.4 Inputs

Worker receives one immutable object.

```text
ContextPackage

Task

Project Summary

Relevant Files

Relevant Symbols

Recent Changes

Constraints

Coding Standards

Tool Manifest
```

No conversation history.

No unrelated files.

---

# 9.5 Outputs

Worker returns:

```text
WorkerResult

Status

Tool Calls

Modified Files

Summary

Diagnostics

Confidence

Metrics
```

---

# 9.6 Worker Lifecycle

```text
Receive Context

↓

Understand Task

↓

Need Information?

↓

Tool Call

↓

Observe Result

↓

Reason

↓

Need Another Tool?

↓

Repeat

↓

Task Complete
```

---

# 9.7 Worker Loop

Every worker executes the same internal loop.

```text
while not finished:

    Observe

    Think

    Act

    Receive Result

    Update Internal State
```

The loop exits only when:

* objective complete
* unrecoverable failure
* retry limit reached
* approval required

---

# 9.8 Internal State

Workers maintain temporary execution state.

```text
Working Memory

Current Objective

Known Files

Open Tool Calls

Current Hypothesis

Pending Actions

Failures
```

Destroyed after task completion.

Workers never persist memory.

---

# 9.9 Internal Reasoning

The worker should continuously answer:

```text
What do I know?

What don't I know?

What tool gives me that information?

What's the next smallest action?
```

Never attempt large edits blindly.

---

# 9.10 Worker State Machine

```text
CREATED

↓

UNDERSTANDING

↓

WAITING_TOOL

↓

THINKING

↓

EDITING

↓

VERIFYING

↓

COMPLETED
```

Failure path:

```text
VERIFYING

↓

FAILED

↓

RETRY
```

---

# 9.11 Tool-Driven Coding

Workers never fabricate file contents.

Instead:

```text
Need Code

↓

Read File

↓

Understand

↓

Edit

↓

Write
```

Never assume.

Always observe first.

---

# 9.12 Read-Before-Write Rule

Every modified file must first be read.

Illegal:

```text
Write auth.py
```

Legal:

```text
Read auth.py

↓

Understand

↓

Write auth.py
```

---

# 9.13 Edit Strategy

Workers should prefer:

```text
Small Patch

↓

Verify

↓

Next Patch
```

Instead of:

```text
Rewrite Entire File
```

Large rewrites increase hallucinations.

---

# 9.14 Patch Model

Workers never return entire files unless necessary.

Preferred representation:

```diff
@@

- old

+ new
```

Tool Executor applies patches.

Advantages:

* Smaller prompts
* Smaller tool payloads
* Better review
* Easier rollback

---

# 9.15 Code Editing Algorithm

Preferred algorithm:

```text
Locate Region

↓

Read Region

↓

Understand

↓

Generate Patch

↓

Apply Patch

↓

Verify

↓

Continue
```

Not:

```text
Rewrite File
```

---

# 9.16 Multi-File Tasks

Worker edits one file at a time.

Example:

```text
auth.py

↓

Verify

↓

routes.py

↓

Verify

↓

frontend.tsx

↓

Verify
```

Never modify ten files simultaneously.

---

# 9.17 Tool Usage Strategy

Workers should minimise tool usage.

Example:

Bad:

```text
Read File

Read File

Read File

Search

Read File
```

Good:

```text
Search Symbol

↓

Read Needed File

↓

Edit
```

---

# 9.18 Tool Categories

Workers may invoke:

Filesystem

```text
Read

Write

Patch

Move

Delete
```

Terminal

```text
Run

Cancel
```

Git

```text
Status

Diff
```

Search

```text
Symbol

Text

File
```

Package

```text
Install

Update
```

Each invocation pauses execution.

---

# 9.19 Verification Strategy

After edits:

```text
Write

↓

Read Back

↓

Compare

↓

Continue
```

Worker should verify its own changes before planner review.

---

# 9.20 Error Handling

If a tool returns:

```text
Compilation Error
```

Worker should:

```text
Read Error

↓

Locate Cause

↓

Patch

↓

Retry
```

Not immediately escalate.

---

# 9.21 Self-Limits

Workers should avoid:

* changing architecture
* introducing dependencies
* deleting unrelated code
* formatting unrelated files
* speculative refactors

Only satisfy the task.

---

# 9.22 Confidence Estimation

Every completed task includes:

```text
Confidence

0–100
```

Factors:

* tests passed
* compilation passed
* assumptions made
* untouched dependencies

Planner uses confidence during review.

---

# 9.23 Retry Behaviour

Worker retries locally before planner involvement.

Example:

```text
Compile Error

↓

Patch

↓

Compile

↓

Patch

↓

Compile
```

Maximum retry count configurable.

Default:

```text
3
```

After that:

Planner intervention.

---

# 9.24 Worker Prompt Structure

Worker prompt:

```text
System

↓

Task

↓

Constraints

↓

Project Summary

↓

Relevant Summaries

↓

Relevant Code

↓

Tool Manifest

↓

Output Schema
```

No conversation history.

---

# 9.25 Tool Manifest

Worker explicitly knows available tools.

Example:

```text
Filesystem

✓

Git

✓

Terminal

✓

Browser

✗

Network

✗
```

Never assume tools exist.

---

# 9.26 Context Expansion

Worker may request additional context.

Example:

```text
Need implementation of:

TokenManager
```

Flow:

```text
Worker

↓

Context Engine

↓

Retrieve

↓

Resume
```

Worker never expands context itself.

---

# 9.27 Command Execution

Worker never executes shell directly.

Instead:

```text
Run Tests

↓

Tool Call

↓

Executor

↓

Terminal

↓

Result
```

---

# 9.28 File Modification Strategy

Preferred order:

```text
Configuration

↓

Backend

↓

Database

↓

Frontend

↓

Tests

↓

Documentation
```

Keeps repository internally consistent.

---

# 9.29 Failure Classification

Failures:

```text
Syntax

Compilation

Runtime

Missing Context

Permission

Tool Failure

Planner Error
```

Each category has different recovery.

---

# 9.30 Worker Metrics

Track:

* reasoning time
* model latency
* tool latency
* edits
* retries
* files modified
* context size
* token usage

Useful for benchmarking.

---

# 9.31 Parallel Workers (Future)

Version 1:

One Worker.

Future:

```text
Planner

↓

Worker A

Worker B

Worker C

↓

Merge
```

Each worker edits isolated files or branches.

---

# 9.32 Design Constraints

1. One worker executes one task.
2. Workers never plan.
3. Workers never access storage directly.
4. Workers never access the filesystem directly.
5. Workers never exceed context budget.
6. Workers always read before writing.
7. Workers produce deterministic tool calls.
8. Workers maintain only ephemeral memory.
9. Workers cannot modify tasks.
10. Workers always terminate.

---

# Architect's Notes (Normative)

## 1. Adopt the ReAct Pattern Internally

Internally, the worker should follow:

```text
Thought

↓

Action

↓

Observation

↓

Thought

↓

Action
```

However, **do not expose chain-of-thought**. The internal reasoning remains private. What is logged should be structured events (e.g. "Read `auth.py`", "Patched `login()`", "Ran tests"), not verbatim reasoning.

---

## 2. Prefer Structured Editing Over Free-Form Text

Instead of asking the model to emit arbitrary prose, define structured actions.

Example internal response schema:

```json
{
  "status": "continue",
  "actions": [
    {
      "tool": "read_file",
      "args": {
        "path": "src/auth.py"
      }
    }
  ],
  "summary": "Need to inspect authentication flow before editing."
}
```

The orchestrator validates this schema before executing anything.

---

## 3. Introduce a Patch Tool

Do **not** rely solely on `write_file`.

Add a first-class tool:

```text
patch_file(
    path,
    search,
    replace
)
```

or an AST-aware equivalent where supported.

Advantages:

* Smaller model outputs
* Fewer merge conflicts
* Easier rollback
* Better audit logs
* Reduced accidental overwrites

For languages with reliable parsers, prefer AST-based transformations over text replacement.

---

## 4. Make Workers Interruptible

Long-running tasks should support interruption.

Between every model invocation and every tool execution, check:

```text
Cancel Requested?

↓

Yes → Save State → Exit

No → Continue
```

This allows users to stop an execution without corrupting the workspace.

---

## 5. Make Workers Observable

Every significant step should emit structured events.

Example:

```text
WorkerStarted

↓

ReadFile(auth.py)

↓

GeneratedPatch

↓

PatchedFile(auth.py)

↓

RunPytest

↓

TestsPassed

↓

WorkerCompleted
```

This enables:

* Live UI progress
* Timeline replay
* Performance analysis
* Debugging failed runs
* Future distributed execution

The Worker Engine should be treated as an execution runtime, not just a prompt wrapped around an LLM.

---