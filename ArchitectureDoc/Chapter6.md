# AI Loom Architecture Specification

# Chapter 6 — Planning Engine

**Version:** 1.0 Draft

---

# 6.1 Purpose

The Planning Engine is the highest-level reasoning component in AI Loom.

Its responsibility is **understanding**, not implementation.

It receives a user objective and produces an executable engineering plan.

It never:

* edits files
* runs shell commands
* executes tools
* writes source code
* modifies the repository

Instead, it thinks like a senior software architect.

---

# 6.2 Responsibilities

The planner is responsible for:

* Understanding user intent
* Understanding the repository
* Identifying affected components
* Estimating complexity
* Breaking work into tasks
* Determining execution order
* Selecting verification strategy
* Choosing worker type
* Detecting ambiguity
* Requesting clarification when necessary

---

# 6.3 Non-Responsibilities

The planner MUST NOT:

* Generate implementation code
* Guess file contents
* Read entire repositories blindly
* Execute shell commands
* Write prompts for tools
* Decide formatting
* Execute tests

Those belong elsewhere.

---

# 6.4 Planner Inputs

The planner receives a **Planning Context**.

```text
PlanningContext

User Objective

Project Summary

Repository Metadata

Relevant Symbols

Relevant Files

Git Status

Current Task History

Configuration

User Constraints
```

It does **not** receive raw source code for the entire project.

---

# 6.5 Planner Outputs

The planner returns a **Plan**.

```text
Plan

Goal

Reasoning Summary

Task Graph

Dependencies

Verification Strategy

Complexity

Risk Assessment

Expected Deliverables
```

The plan becomes the input for the Scheduler.

---

# 6.6 Planner Workflow

```text
User Request

↓

Understand Intent

↓

Inspect Repository

↓

Locate Relevant Components

↓

Estimate Scope

↓

Generate Tasks

↓

Build Dependency Graph

↓

Define Verification

↓

Return Plan
```

---

# 6.7 Planning Levels

Every request is classified.

### Level 0

Simple

Examples:

* Rename variable
* Fix typo
* Update README

Planner creates:

One Task.

---

### Level 1

Medium

Examples:

* Add API endpoint
* Create React page
* Add configuration option

Planner creates:

2–10 Tasks.

---

### Level 2

Large Feature

Examples:

* Add Authentication
* Add Payments
* Add Notifications

Planner creates:

10–40 Tasks.

---

### Level 3

Architecture

Examples:

* Migrate Flask to FastAPI
* Convert JS to TS
* Monolith to Microservices

Planner creates:

Multiple phases.

---

# 6.8 Intent Classification

Planner first classifies intent.

Supported intents:

```text
CREATE

MODIFY

FIX

REFACTOR

OPTIMIZE

TEST

DOCUMENT

ANALYZE

EXPLAIN

SEARCH

DELETE

MIGRATE
```

This determines planning strategy.

---

# 6.9 Repository Inspection

Planner queries the Index Service.

It asks:

* Which files are relevant?
* Which symbols are involved?
* Which frameworks exist?
* What architecture is used?

It does NOT scan the filesystem directly.

---

# 6.10 Complexity Estimation

Complexity is estimated before decomposition.

Factors:

* Files affected
* Symbols affected
* Cross-module dependencies
* External packages
* Framework complexity
* Estimated token count
* Number of worker iterations

Levels:

```text
TRIVIAL

LOW

MEDIUM

HIGH

EXTREME
```

---

# 6.11 Task Decomposition

Good decomposition:

```text
Add OAuth Login

↓

Create OAuth Config

↓

Backend Callback

↓

Database Changes

↓

Frontend Button

↓

Testing
```

Bad decomposition:

```text
Implement OAuth

(one task)
```

Tasks should be independently executable.

---

# 6.12 Task Rules

Every task must satisfy:

* One objective
* One owner
* Small enough for one worker
* Clearly verifiable
* Independent where possible
* Deterministic output

---

# 6.13 Dependency Generation

Planner creates edges.

Example:

```text
Database Schema

↓

Repository

↓

Service

↓

API

↓

Frontend
```

Scheduler executes according to dependencies.

---

# 6.14 File Selection

Planner never sends entire repositories.

Instead:

```text
User Request

↓

Index Query

↓

Relevant Symbols

↓

Relevant Files

↓

Context Package
```

Maximum files determined by context budget.

---

# 6.15 Context Budgeting

Planner estimates required context.

Example:

```text
Task

↓

Estimated Tokens

↓

Maximum Context

↓

File Selection

↓

Worker
```

If budget exceeded:

* Summaries replace files.
* Planner creates smaller tasks.

---

# 6.16 Clarification Strategy

Planner requests clarification only when required.

Examples:

* Multiple valid interpretations
* Missing framework choice
* Missing target directory
* Conflicting requirements

Never ask unnecessary questions.

---

# 6.17 Risk Assessment

Each plan includes:

```text
Risk

LOW

MEDIUM

HIGH
```

High-risk examples:

* Database migrations
* File deletion
* Dependency upgrades
* Massive refactors

Risk influences approval requirements.

---

# 6.18 Verification Strategy

Planner defines verification before execution.

Possible checks:

* Unit tests
* Integration tests
* Build succeeds
* Linter passes
* Formatter
* Type checker
* Manual review

Workers do not decide this.

---

# 6.19 Worker Selection

Planner chooses worker profile.

Version 1:

```text
Coding Worker
```

Future:

```text
Testing Worker

Documentation Worker

Security Worker

Refactoring Worker

Performance Worker
```

---

# 6.20 Model Selection

Planner requests capability.

Not model names.

Example:

```text
Requires:

High Reasoning

Medium Context

Creative = Low
```

Model Router chooses the actual model.

This prevents planner-model coupling.

---

# 6.21 Planning Constraints

Planner must respect:

* Context limit
* Permission policy
* User instructions
* Workspace boundaries
* Existing coding standards

---

# 6.22 Incremental Planning

Large projects should not produce thousands of tasks immediately.

Instead:

```text
High-Level Plan

↓

Execute Phase

↓

Re-plan

↓

Execute Next Phase
```

This keeps planning adaptive.

---

# 6.23 Failure Recovery

If Worker repeatedly fails:

```text
Worker

↓

Failure

↓

Planner

↓

Reanalyse

↓

Split Task

↓

Retry
```

Planner may completely replace a task.

---

# 6.24 Prompt Structure

Planner prompt consists of:

```text
System Instructions

↓

Architecture Summary

↓

User Objective

↓

Repository Summary

↓

Relevant Metadata

↓

Output Schema
```

Never include unnecessary code.

---

# 6.25 Planner Output Schema

Every plan follows:

```text
Goal

Assumptions

Tasks

Dependencies

Required Files

Relevant Symbols

Verification

Estimated Complexity

Risks

Notes
```

Machine-readable.

---

# 6.26 Planning Heuristics

The planner follows these heuristics:

1. Read less.
2. Split more.
3. Prefer deterministic tasks.
4. Minimise worker context.
5. Reuse existing code.
6. Preserve architecture.
7. Avoid unnecessary files.
8. Avoid unnecessary dependencies.
9. Verify everything.
10. Ask the user only when essential.

---

# 6.27 Example

Input:

```text
Add JWT Authentication
```

Planner output:

```text
Goal

Add JWT authentication.

Tasks

1. Locate auth system.
2. Create JWT configuration.
3. Implement token generation.
4. Add authentication middleware.
5. Protect routes.
6. Update frontend login.
7. Write tests.
8. Verify.

Dependencies

1 → 2

2 → 3

3 → 4

4 → 5

5 → 6

6 → 7

7 → Review
```

---

# 6.28 Performance Goals

Planner should:

* Read fewer than 20 files for most tasks.
* Produce plans in under 15 seconds (hardware dependent).
* Never exceed planner context budget.
* Generate deterministic task graphs for identical inputs.

---

# 6.29 Future Extensions

The Planning Engine is designed to support:

* Cost-aware planning
* Multi-worker parallel scheduling
* Automatic milestone generation
* Long-running projects
* Repository-wide refactors
* Cross-repository planning
* Multi-language dependency planning

No architectural changes are required to support these.

---

# 6.30 Design Constraints

1. Planner never writes code.
2. Planner never executes tools.
3. Planner always works from indexed project data first.
4. Planner produces executable, verifiable tasks.
5. Planner is stateless outside `ExecutionState`.
6. Planner requests capabilities, not concrete model names.
7. Planner favours smaller, independent tasks over large monolithic ones.
8. Planner never exceeds the configured context budget.

---

## **Architect's Notes (Normative)**

These are mandatory design decisions for AI Loom Version 1.

### 1. Hierarchical Planning

Do **not** generate the full execution graph for very large requests.

Instead:

```text
User Request
      │
      ▼
High-Level Milestones
      │
      ▼
Expand Current Milestone
      │
      ▼
Execute
      │
      ▼
Expand Next Milestone
```

This keeps planner cost nearly constant regardless of repository size.

---

### 2. Planning Memory

The planner should maintain a lightweight **planning memory**, separate from conversation history.

Example:

```text
Completed Milestones

Known Constraints

User Decisions

Open Questions

Architectural Decisions
```

This prevents re-planning from forgetting earlier decisions.

---

### 3. Stable Task IDs

Task IDs should never change.

Example:

```text
AUTH-001

AUTH-002

AUTH-003
```

Instead of:

```text
Task 1

Task 2
```

Stable IDs make retries, checkpoints, logging and UI significantly easier.

---

### 4. Deterministic Plans

The same repository and the same prompt should produce nearly identical plans.

Randomness in planning should be kept close to zero.

Planner temperature should therefore be very low (typically 0–0.2).

---