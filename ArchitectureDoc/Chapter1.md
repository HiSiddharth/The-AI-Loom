
# AI Loom Architecture Specification

## Chapter 1 — Vision, Philosophy & Design Principles

**Version:** 1.0 Draft

---

# 1. Introduction

AI Loom is an **agentic software engineering platform** designed to orchestrate multiple local Large Language Models (LLMs) into a single intelligent coding agent.

Unlike traditional AI assistants that keep a single conversation with one model, AI Loom treats software engineering as a graph of independent tasks.

Every task is:

* Planned
* Assigned
* Executed
* Verified
* Integrated

independently.

This dramatically reduces context size while increasing reliability.

---

# 2. Problem Statement

Current coding assistants suffer from several issues.

### Huge Context Windows

Most agents continuously append messages.

```
User
↓

Plan

↓

Code

↓

Fix

↓

Explain

↓

Refactor

↓

More fixes
```

Eventually the model is processing tens of thousands of unnecessary tokens.

Problems:

* Slow
* Expensive
* Hallucinations
* Context pollution

---

### One Model Does Everything

A single model is expected to:

* Understand architecture
* Write code
* Debug
* Review
* Plan
* Test

These require different strengths.

---

### Poor Context Selection

Most agents simply dump many files into the prompt.

Instead, they should discover which files are actually relevant.

---

### Lack of Verification

Many agents stop after generating code.

Software engineering requires:

* Compilation
* Tests
* Linting
* Review

before completion.

---

# 3. Vision

AI Loom should behave like a competent software engineer.

When asked:

> Build me a weather dashboard.

It should internally think:

```
Understand project

↓

Find technologies

↓

Create plan

↓

Split work

↓

Implement frontend

↓

Implement backend

↓

Run tests

↓

Review

↓

Fix

↓

Deliver
```

The user sees only progress.

---

# 4. Core Philosophy

## Principle 1

### Small Contexts Beat Huge Contexts

Never send unnecessary files.

Instead:

```
Whole Project

↓

Index

↓

Find relevant symbols

↓

Read only required files

↓

Solve
```

---

## Principle 2

### Intelligence is Expensive

Use the smartest model only when needed.

Example:

Planner

↓

27B

Worker

↓

9B

Reviewer

↓

27B

---

## Principle 3

### Every Task is Independent

Workers never inherit the entire conversation.

Each worker starts with:

* objective
* relevant files
* constraints
* coding style

Nothing else.

---

## Principle 4

### Tools over Hallucination

Never ask a model to remember code.

Instead use tools.

Good:

```
Read file

Search symbol

Run tests

Git diff
```

Bad:

```
Remember entire repository
```

---

## Principle 5

### AI Never Directly Changes Files

Models produce tool calls.

Python executes them.

Model:

```
Write file:

main.py
```

Python:

```
validate

↓

backup

↓

write

↓

index
```

---

## Principle 6

### Every Result Must Be Verified

No code reaches completion without validation.

Verification pipeline:

```
Worker

↓

Formatter

↓

Lint

↓

Tests

↓

Reviewer

↓

Success
```

---

# 5. Primary Goals

Version 1 should achieve:

✅ Local only

✅ No cloud dependency

✅ LM Studio backend

✅ OpenAI compatible API

✅ LangGraph orchestration

✅ Automatic planning

✅ Task decomposition

✅ Incremental indexing

✅ Symbol search

✅ Terminal execution

✅ Git support

✅ Streaming responses

✅ Automatic retries

---

# 6. Non Goals

Version 1 will NOT include:

❌ Distributed execution

❌ Multi-user server

❌ Fine tuning

❌ Long-term conversational memory

❌ Autonomous internet browsing

❌ Voice assistant

These may be added later.

---

# 7. Success Criteria

A successful AI Loom should be able to:

Example 1

```
User:

Build a Flask API.
```

Without further prompting it should:

Plan

↓

Create project

↓

Generate code

↓

Install packages

↓

Run

↓

Fix errors

↓

Deliver

---

Example 2

```
User:

Add OAuth login.
```

AI Loom should:

Locate authentication

↓

Locate routes

↓

Locate frontend

↓

Create plan

↓

Modify only affected files

↓

Run tests

↓

Verify

↓

Return

---

Example 3

```
User:

Why is startup slow?
```

It should:

Analyze project

↓

Locate bottlenecks

↓

Profile if needed

↓

Recommend fixes

↓

Implement approved fixes

---

# 8. Guiding Metrics

The architecture should optimize for:

### Accuracy

Correct code over fast code.

---

### Context Efficiency

Few relevant tokens instead of massive prompts.

---

### Recoverability

Every action should be undoable.

---

### Transparency

The user should always know:

Current task

Current worker

Current files

Current command

Current progress

---

### Extensibility

Adding new models or tools should require minimal changes.

---

# 9. Long-Term Vision (v3+)

Although Version 1 targets local coding, the architecture should naturally extend to:

* Multi-model orchestration
* Multiple concurrent workers
* Remote execution
* CI/CD integration
* IDE plugins
* Browser automation
* Documentation generation
* Codebase learning
* Team memory
* MCP servers
* Plugin ecosystem

This is why AI Loom will use a modular architecture from day one.

---

# 10. Architecture Motto

> **"Think deeply, act deliberately, verify everything, and only read what you need."**

This single sentence should guide every architectural decision in AI Loom.

---