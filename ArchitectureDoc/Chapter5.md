# AI Loom Architecture Specification

# Chapter 5 — Execution Engine & LangGraph Workflow

**Version:** 1.0 Draft

---

# 5.1 Purpose

This chapter defines the execution engine that powers AI Loom.

Unlike a chatbot, AI Loom is a **workflow engine**. Every user request becomes a directed graph of tasks managed by LangGraph.

The execution engine is responsible for:

* Task orchestration
* State transitions
* Retry handling
* Worker scheduling
* Checkpointing
* Recovery
* Human approval
* Progress tracking

The execution engine **never performs reasoning itself**. It only coordinates components.

---

# 5.2 Why LangGraph?

Software development is not a conversation.

It is a workflow.

Example:

```text
Build REST API

↓

Design

↓

Create Models

↓

Create Routes

↓

Create Tests

↓

Run Tests

↓

Fix

↓

Review

↓

Done
```

Traditional chat systems cannot naturally represent branching, retries, or dependencies.

LangGraph models these workflows as a state machine.

---

# 5.3 Graph Overview

Every request becomes one execution graph.

```text
               User Request
                     │
                     ▼
             Initialize Session
                     │
                     ▼
             Project Discovery
                     │
                     ▼
                 Planning
                     │
             ┌───────┴────────┐
             ▼                ▼
         Simple          Multi Task
             │                │
             └───────┬────────┘
                     ▼
             Task Scheduling
                     │
                     ▼
                Execute Task
                     │
         ┌───────────┼────────────┐
         ▼           ▼            ▼
     Success      Retry       Approval
         │           │            │
         └──────┬────┴────────────┘
                ▼
          Verification
                │
        ┌───────┴─────────┐
        ▼                 ▼
     Accept           Re-plan
        │                 │
        └────────┬────────┘
                 ▼
             Final Report
```

---

# 5.4 Global Workflow State

LangGraph owns a single immutable state object.

```text
ExecutionState

session

workspace

conversation

memory

project

plan

task_graph

active_task

worker_result

review_result

events

metrics

configuration
```

Each node receives the current state and returns an updated state.

Nodes never mutate shared state directly.

---

# 5.5 Workflow Nodes

Version 1 defines these nodes.

```text
InitializeNode

DiscoveryNode

PlanningNode

ScheduleNode

WorkerNode

ToolNode

ReviewNode

RetryNode

ApprovalNode

CheckpointNode

FinishNode

FailureNode
```

Each node has exactly one responsibility.

---

# 5.6 Initialize Node

Purpose:

Create execution environment.

Responsibilities:

* Create session
* Load configuration
* Create workspace
* Initialize event stream
* Initialize metrics
* Restore checkpoint if requested

Output:

```text
Session Ready
```

---

# 5.7 Discovery Node

Purpose:

Understand the project before planning.

Responsibilities:

* Detect language
* Detect framework
* Read project summary
* Query symbol database
* Read configuration files
* Build Project object

Does NOT invoke an LLM.

Uses:

* Tree-sitter
* SQLite
* Git
* File scanner

---

# 5.8 Planning Node

Purpose:

Convert user objective into executable tasks.

Input:

```text
Create authentication system
```

Output:

```text
Task A

Task B

Task C

Dependencies
```

Responsibilities:

* Estimate complexity
* Decompose work
* Select worker type
* Estimate context
* Define verification strategy

Uses Planner Model.

---

# 5.9 Scheduler Node

Receives:

```text
TaskGraph
```

Produces:

```text
Execution Queue
```

Scheduling Rules:

* Execute only READY tasks.
* Block dependent tasks.
* Respect retry limits.
* Future support for parallel execution.

---

# 5.10 Worker Node

The Worker Node is responsible for executing one task.

Input:

```text
ContextPackage
```

Output:

```text
WorkerResult
```

Responsibilities:

* Build prompt
* Invoke worker model
* Parse tool calls
* Stream reasoning
* Collect output

The Worker Node never executes tools itself.

---

# 5.11 Tool Node

Receives ToolCalls.

Example:

```text
Read File

Write File

Run Terminal

Git Diff
```

Responsibilities:

* Validate request
* Check permissions
* Execute tool
* Capture output
* Return ToolResult

The Worker pauses while waiting for tool execution.

---

# 5.12 Review Node

Purpose:

Verify completed work.

Checks:

* Objective satisfied
* No syntax errors
* No missing files
* Coding standards followed
* Tests pass
* Planner approves

Possible outcomes:

```text
Approved

Retry

Escalate

Human Approval
```

---

# 5.13 Retry Node

Receives failed tasks.

Responsibilities:

* Count retries
* Modify prompt
* Provide error context
* Select retry strategy

Strategies:

```text
Same Prompt

Different Prompt

Different Model

Smaller Context

Planner Intervention
```

---

# 5.14 Approval Node

Some actions require user approval.

Examples:

```text
Delete Files

Install Packages

Git Commit

Run Network Commands

Modify Outside Workspace
```

Workflow pauses until response.

---

# 5.15 Checkpoint Node

Purpose:

Persist workflow state.

Checkpoint after:

* Planning
* Every completed task
* Review
* User approval
* Session end

Allows crash recovery.

---

# 5.16 Finish Node

Produces:

ExecutionReport

Responsibilities:

* Collect metrics
* Generate summary
* Close session
* Persist logs
* Stream completion

---

# 5.17 Failure Node

Entered when recovery fails.

Responsibilities:

* Save state
* Record failure
* Generate diagnostics
* Return partial progress

No work is lost.

---

# 5.18 State Transitions

```text
CREATED

↓

DISCOVERING

↓

PLANNING

↓

SCHEDULING

↓

EXECUTING

↓

VERIFYING

↓

COMPLETED
```

Alternative transitions:

```text
EXECUTING

↓

FAILED

↓

RETRYING

↓

EXECUTING
```

or

```text
EXECUTING

↓

WAITING_APPROVAL

↓

EXECUTING
```

---

# 5.19 Task State Machine

Every Task follows this lifecycle.

```text
CREATED

↓

READY

↓

RUNNING

↓

WAITING_TOOL

↓

RUNNING

↓

REVIEW

↓

COMPLETED
```

Failure path:

```text
RUNNING

↓

FAILED

↓

RETRY

↓

RUNNING
```

---

# 5.20 Execution Queue

The scheduler maintains:

```text
Ready Queue

Blocked Queue

Retry Queue

Completed Queue

Failed Queue
```

Only the Ready Queue is eligible for execution.

---

# 5.21 Dependency Resolution

Example:

```text
Create DB Schema

↓

Repository Layer

↓

API Layer

↓

Frontend
```

The scheduler automatically unlocks tasks whose dependencies are satisfied.

---

# 5.22 Context Generation

Before every Worker invocation:

```text
Task

↓

Relevant Files

↓

Relevant Symbols

↓

Recent Changes

↓

Coding Style

↓

Prompt

↓

Worker
```

This happens every time.

Workers never inherit previous prompts.

---

# 5.23 Tool Loop

Workers may require multiple tool invocations.

```text
Worker

↓

Read File

↓

Worker

↓

Search Symbol

↓

Worker

↓

Write File

↓

Worker

↓

Done
```

The worker is paused and resumed between tool calls.

---

# 5.24 Planner Intervention

If retries exceed threshold:

```text
Worker

↓

Failure

↓

Planner

↓

Re-plan

↓

New Task

↓

Worker
```

Planner is expensive.

Only invoked when necessary.

---

# 5.25 Human Intervention

The graph supports explicit pause points.

```text
Delete Folder

↓

Pause

↓

Await User

↓

Resume
```

Execution resumes from the same state.

---

# 5.26 Checkpoint Strategy

Checkpoint after:

```text
Planning

Task Completion

Review

Approval

Finish
```

Never checkpoint during tool execution.

---

# 5.27 Event Generation

Every node emits events.

Example:

```text
PlanningStarted

PlanningFinished

WorkerStarted

ToolRequested

ToolCompleted

ReviewStarted

ReviewPassed

TaskFinished
```

Events drive:

* Logs
* UI
* Metrics
* Debugging

---

# 5.28 Cancellation

Cancellation is cooperative.

When user requests cancellation:

```text
Cancel Requested

↓

Finish Current Tool

↓

Save Checkpoint

↓

Terminate Worker

↓

Close Session
```

No abrupt process termination.

---

# 5.29 Recovery

If AI Loom crashes:

```text
Load Checkpoint

↓

Restore Graph

↓

Restore Task Queue

↓

Resume Worker
```

No task should be repeated unless explicitly required.

---

# 5.30 Concurrency (Future)

Version 1:

One active Worker.

Future:

```text
Planner

↓

Scheduler

├── Worker 1

├── Worker 2

├── Worker 3

└── Worker 4
```

Each worker receives independent contexts.

Shared state is synchronized only through completed task results.

---

# 5.31 Execution Timeline

Typical execution:

```text
User Prompt

↓

Initialize

↓

Discover Project

↓

Planner

↓

Scheduler

↓

Worker

↓

Tools

↓

Worker

↓

Review

↓

Retry (optional)

↓

Finish

↓

Report
```

---

# 5.32 Design Constraints

1. Every node has exactly one responsibility.
2. Nodes communicate only through ExecutionState.
3. Workers never execute tools directly.
4. Planner never edits files.
5. Scheduler never invokes models.
6. Tool execution is deterministic.
7. Every transition is logged.
8. Every node is independently testable.
9. Every workflow is resumable.
10. Every failure has a recovery path.

---

# 5.33 Future Graph Extensions

The execution engine is designed to support additional nodes without changing the core architecture.

Potential additions include:

* Documentation Node
* Benchmark Node
* Security Audit Node
* Refactoring Node
* Performance Profiling Node
* CI/CD Node
* Browser Automation Node
* MCP Node
* Multi-Agent Collaboration Node

These are inserted into the graph as independent nodes while preserving the same execution model.

---

