# AI Loom Architecture Specification

# Chapter 14 — Observability, Logging & Telemetry

**Version:** 1.0 Draft

---

# 14.1 Purpose

The Observability System provides complete visibility into AI Loom's behaviour.

Unlike traditional AI assistants, AI Loom is expected to execute hundreds of tool calls, make thousands of decisions and run for extended periods.

Every significant action must therefore be observable.

The goal is to answer questions such as:

* Why did the agent make this decision?
* Which model performed each task?
* Which files were modified?
* Why did a task fail?
* How much context was used?
* Where was time spent?

---

# 14.2 Design Philosophy

Observability follows four principles:

1. Every important event is recorded.
2. Events are structured, not free-form text.
3. Logs explain *what* happened, not private model reasoning.
4. Every event can be traced back to its originating task.

---

# 14.3 Components

```text
                    Event Bus
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
    Event Log      Metrics Store     Live UI
        │               │               │
        ▼               ▼               ▼
    Timeline       Performance     Dashboard
```

Everything emits events.

Nothing writes directly to log files.

---

# 14.4 Event Sources

Every subsystem emits events.

```text
Planner

Worker

Context Engine

Indexer

Tool Engine

Model Router

Permission Manager

Memory System
```

---

# 14.5 Event Object

Every event has the same schema.

```text
Event

id

timestamp

session_id

task_id

component

event_type

severity

payload

duration

metadata
```

---

# 14.6 Event Categories

Examples:

```text
Lifecycle

Planning

Tool

Filesystem

Model

Context

Memory

Security

Performance

Error
```

---

# 14.7 Lifecycle Events

Examples:

```text
SessionStarted

PlannerStarted

WorkerStarted

TaskCompleted

SessionCompleted

Cancelled
```

---

# 14.8 Planning Events

Examples:

```text
PlanGenerated

TaskCreated

TaskAssigned

TaskCompleted

TaskRejected

PlanRevised
```

---

# 14.9 Tool Events

Examples:

```text
ToolRequested

ValidationPassed

ExecutionStarted

ExecutionCompleted

ExecutionFailed
```

---

# 14.10 Model Events

Examples:

```text
InferenceRequested

ModelSelected

InferenceStarted

InferenceCompleted

FallbackTriggered

ProviderUnavailable
```

---

# 14.11 Context Events

Examples:

```text
ContextRetrieved

ContextCompressed

BudgetExceeded

AdditionalContextRequested
```

---

# 14.12 Memory Events

Examples:

```text
MemoryCreated

MemoryUpdated

MemoryRetrieved

MemoryArchived

MemoryExpired
```

---

# 14.13 Security Events

Examples:

```text
PermissionGranted

PermissionDenied

WorkspaceEscapeBlocked

ApprovalRequested

SecretDetected
```

---

# 14.14 Error Events

Examples:

```text
ModelFailure

ToolFailure

ParsingFailure

ValidationFailure

Timeout

InternalError
```

Errors should include structured diagnostics.

---

# 14.15 Event Severity

```text
TRACE

DEBUG

INFO

WARNING

ERROR

CRITICAL
```

Default:

Most events use **INFO**.

---

# 14.16 Event Flow

```text
Component

↓

Create Event

↓

Event Bus

↓

Subscribers

↓

Storage

↓

Dashboard
```

Events should never block execution.

---

# 14.17 Timeline View

A session timeline might appear as:

```text
12:00 Session Started

12:00 Planner Started

12:00 Plan Generated

12:01 Worker Started

12:01 Read auth.py

12:02 Patch Applied

12:03 Tests Passed

12:03 Task Completed

12:04 Session Completed
```

This is intended for humans.

---

# 14.18 Metrics

Metrics are numerical summaries rather than events.

Examples:

```text
Tasks Completed

Files Modified

Inference Count

Average Tool Latency

Average Tokens

Success Rate

Retry Count
```

---

# 14.19 Performance Metrics

Collect:

```text
Planning Time

Worker Time

Model Latency

Tool Latency

Index Latency

Retrieval Time

Patch Time
```

Allows bottleneck analysis.

---

# 14.20 Token Metrics

Per inference:

```text
Prompt Tokens

Completion Tokens

Total Tokens

Context Budget

Unused Budget
```

Useful for optimisation.

---

# 14.21 Model Metrics

Track:

```text
Model Name

Provider

Latency

Tokens/sec

Failures

Fallback Count
```

Useful for routing improvements.

---

# 14.22 Tool Metrics

Track:

```text
Tool Name

Duration

Success Rate

Retry Count

Failure Rate
```

Allows optimisation of slow tools.

---

# 14.23 Context Metrics

Track:

```text
Retrieved Symbols

Retrieved Files

Compression Ratio

Context Size

Unused Context
```

Helps improve retrieval quality.

---

# 14.24 Worker Metrics

Track:

```text
Iterations

Tool Calls

Files Edited

Retries

Confidence

Completion Time
```

Useful for benchmarking.

---

# 14.25 Planner Metrics

Track:

```text
Tasks Generated

Average Task Size

Plan Revisions

Task Success Rate

Average Review Score
```

---

# 14.26 Dashboard

Recommended dashboard panels:

```text
Current Session

Current Task

Running Worker

Tool Activity

Model Usage

Recent Events

Errors

Performance Graphs
```

Dashboard consumes events only.

---

# 14.27 Log Storage

Suggested storage:

```text
SQLite

events

metrics

sessions

performance

errors
```

Large deployments may later migrate to dedicated observability systems.

---

# 14.28 Event Correlation

Every event includes:

```text
Session ID

Task ID

Worker ID

Request ID
```

This allows reconstruction of complete execution chains.

---

# 14.29 Privacy

Never log:

* Prompt chain-of-thought
* Secrets
* API keys
* Passwords
* Private environment variables

Sensitive values should be redacted before storage.

---

# 14.30 Structured Errors

Instead of:

```text
Something went wrong.
```

Return:

```text
ToolFailure

Tool:
pytest

Exit Code:
1

Duration:
3.1 s

Reason:
ImportError
```

Machine-readable errors simplify recovery.

---

# 14.31 Event Replay

Future capability:

```text
Stored Events

↓

Replay Engine

↓

Visual Timeline
```

Useful for debugging complex failures.

---

# 14.32 Sampling

Verbose events (TRACE/DEBUG) may be sampled or disabled in production.

Critical events must never be sampled.

---

# 14.33 Extensibility

New components only need to:

1. Define event types.
2. Publish to the Event Bus.

No changes to storage or dashboard should be required.

---

# 14.34 Performance Targets

| Operation         |   Target |
| ----------------- | -------: |
| Publish Event     |   < 1 ms |
| Retrieve Timeline | < 100 ms |
| Metric Update     |   < 2 ms |
| Dashboard Refresh | < 500 ms |

Observability should have minimal impact on execution.

---

# 14.35 Design Constraints

1. Events are immutable.
2. Events never contain private model reasoning.
3. Logging must never block execution.
4. Every task is fully traceable.
5. Metrics are derived from events whenever practical.
6. Logs are append-only.
7. Sensitive data is redacted.
8. Event schemas are versioned.
9. Every subsystem publishes events.
10. Observability is always enabled, though verbosity may vary.

---

# Architect's Notes (Normative)

## 1. Use Event Sourcing Internally

Treat events as the primary record of execution.

Current state (running task, worker progress, dashboard) should be derivable from the event stream rather than relying on mutable global state.

---

## 2. Separate Logs, Metrics and Traces

Keep these concepts independent.

**Logs**

```text
WorkerStarted
```

**Metrics**

```text
Worker Duration = 18.2 s
```

**Trace**

```text
Planner

↓

Worker

↓

Tool

↓

Model
```

Mixing them makes analysis much harder.

---

## 3. Adopt Distributed Tracing Concepts

Even though AI Loom is initially a local application, structure events as if components were distributed services.

Example trace:

```text
Planner

↓

Context Engine

↓

Worker

↓

Tool Engine

↓

Model Router

↓

LM Studio
```

This makes future scaling to multiple machines almost effortless.

---

## 4. Build a Live Event Stream

Instead of polling SQLite, expose a publish/subscribe event stream.

Future UI components can subscribe to:

* planner events
* worker events
* model events
* tool events
* security events

This enables real-time dashboards and progress updates.

---

## 5. Design for Debuggability

One of AI Loom's defining strengths should be that every decision can be explained through observable events.

A user should be able to answer questions like:

* "Why did the Worker read this file?"
* "Why did the Router choose the 27B model?"
* "Why was this command rejected?"
* "Why did planning take 12 seconds?"

without relying on hidden model reasoning.

This level of transparency will make AI Loom significantly easier to trust, debug and extend than most existing AI coding agents.

---

