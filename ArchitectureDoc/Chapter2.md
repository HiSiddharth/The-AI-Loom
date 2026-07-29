# AI Loom Architecture Specification

# Chapter 2 — High-Level System Architecture

**Version:** 1.0 Draft

---

# 2.1 Purpose

This chapter defines the complete architecture of AI Loom from a systems perspective.

It answers:

* What processes exist?
* How do they communicate?
* Which component owns what responsibility?
* How does a user request become working code?
* Where is state stored?
* Where are models invoked?
* Where are tools executed?

The goal is that every subsequent chapter expands one box from this architecture.

---

# 2.2 System Overview

AI Loom consists of seven major subsystems.

```text
                    User
                      │
                      ▼
              OpenCode / IDE / API
                      │
                      ▼
          AI Loom OpenAI-Compatible Server
                      │
 ┌────────────────────┼────────────────────┐
 │                    │                    │
 ▼                    ▼                    ▼
Session Manager   Event Stream      Configuration
                      │
                      ▼
               LangGraph Runtime
                      │
      ┌───────────────┼────────────────┐
      ▼               ▼                ▼
 Planner         Task Scheduler     Memory
      │
      ▼
Execution Graph
      │
      ▼
Workers
      │
      ▼
Tool Executor
      │
 ┌────┼─────┬──────────┬──────────┬──────────┐
 ▼    ▼     ▼          ▼          ▼
FS  Terminal Git   Project Index Model Router
                    │
                    ▼
              LM Studio API
                    │
      ┌─────────────┴──────────────┐
      ▼                            ▼
Qwen 27B Planner            Qwen 9B Worker
```

---

# 2.3 Component Responsibilities

## Client Layer

Responsible for interacting with users.

Supported clients:

* OpenCode
* VS Code Extension (future)
* Web UI (future)
* REST API
* CLI

Responsibilities:

* Receive prompts
* Display streaming output
* Show progress
* Display logs
* Render diffs

No business logic exists here.

---

## AI Loom Server

Acts as the gateway.

Responsibilities:

* OpenAI-compatible API
* Session creation
* Authentication (future)
* Streaming
* Request validation
* Configuration loading

It never performs planning.

---

## Session Manager

Each user interaction becomes a Session.

A Session owns:

```text
Session ID

Workspace

Conversation

Task Graph

Memory

Configuration

Permissions

Progress

Logs
```

Sessions are isolated.

Nothing is shared unless explicitly configured.

---

## Event Bus

All components communicate through events.

Example:

```text
TaskCreated

↓

WorkerStarted

↓

FileWritten

↓

TestsPassed

↓

TaskCompleted
```

Every component emits events.

Nothing directly manipulates another subsystem.

---

## LangGraph Runtime

The brain of AI Loom.

Owns:

* execution graph
* retries
* branching
* state
* checkpoints

LangGraph never edits files.

It only decides what happens next.

---

## Planner

Uses the largest available reasoning model.

Responsibilities:

* understand request
* inspect project
* create dependency graph
* estimate complexity
* assign workers
* verify results

The planner never writes code.

---

## Scheduler

Receives the execution graph.

Example:

```text
Task A

↓

Task B

↓

Task C
```

or

```text
Task A

├── Task B

├── Task C

└── Task D
```

Independent tasks may execute simultaneously in future versions.

---

## Worker

Workers execute exactly one task.

Inputs:

* objective
* constraints
* selected files
* coding style
* relevant summaries

Outputs:

* tool calls
* explanation
* completion status

Workers never know about unrelated tasks.

---

## Tool Executor

Workers cannot access the operating system directly.

Instead:

```text
Worker

↓

Tool Call

↓

Validation

↓

Execution

↓

Result
```

Every tool passes through the Tool Executor.

---

## Model Router

Owns every LLM invocation.

Responsibilities:

* choose model
* load model
* unload model
* batching
* retry
* streaming

The rest of AI Loom never knows which model is running.

---

## Project Intelligence

Maintains knowledge of the repository.

Contains:

* symbol index
* dependency graph
* summaries
* embeddings
* file metadata

This subsystem answers questions like:

"What files implement login?"

without involving an LLM.

---

## Storage

Persistent storage.

Contains:

```text
SQLite

Workspace Cache

Logs

Snapshots

Indexes

Configuration
```

No source code is permanently duplicated.

Only metadata is stored.

---

# 2.4 Runtime Processes

Version 1 contains three long-running processes.

## Process 1

AI Loom Server

Responsibilities:

* HTTP API
* WebSocket
* streaming

---

## Process 2

Model Manager

Responsibilities:

* communicate with LM Studio
* load models
* unload models
* health monitoring

Future versions may replace LM Studio with Ollama or vLLM.

---

## Process 3

Worker Runtime

Responsible for:

* LangGraph
* tools
* indexing
* execution

Separating these prevents model loading from blocking orchestration.

---

# 2.5 Request Lifecycle

A complete execution.

```text
User

↓

OpenCode

↓

POST /chat

↓

Session Manager

↓

Planner

↓

Project Index

↓

Task Graph

↓

Scheduler

↓

Worker

↓

Tool Calls

↓

File Changes

↓

Tests

↓

Review

↓

Merge

↓

Response
```

---

# 2.6 Internal Layers

AI Loom follows strict layering.

```text
Presentation

↓

API

↓

Orchestration

↓

Intelligence

↓

Execution

↓

Infrastructure
```

---

## Presentation

Only UI.

Cannot execute tools.

---

## API

Owns REST.

Cannot perform planning.

---

## Orchestration

Owns workflow.

Cannot edit files.

---

## Intelligence

Owns LLM reasoning.

Cannot access filesystem.

---

## Execution

Owns tools.

Cannot plan.

---

## Infrastructure

Owns:

* SQLite
* LM Studio
* filesystem
* terminal

Contains no AI logic.

---

# 2.7 Communication Rules

Allowed:

Planner

↓

Worker

↓

Tool Executor

↓

Filesystem

Not allowed:

Planner

✗

Filesystem

---

Worker

✗

LM Studio

Worker always asks the Model Router.

---

Planner

✗

SQLite

Planner uses repositories/services.

No component accesses storage directly except infrastructure adapters.

---

# 2.8 Dependency Direction

Dependencies always point downward.

```text
UI

↓

API

↓

Graph

↓

Workers

↓

Tools

↓

Infrastructure
```

Infrastructure never imports orchestration.

This prevents circular dependencies.

---

# 2.9 Data Ownership

Every type has one owner.

| Data           | Owner                |
| -------------- | -------------------- |
| Session        | Session Manager      |
| Task Graph     | Planner              |
| Workflow State | LangGraph            |
| Tool Calls     | Tool Executor        |
| Models         | Model Router         |
| Symbols        | Project Intelligence |
| Configuration  | Config Manager       |
| Logs           | Event Bus            |
| Workspace      | Filesystem Service   |

No duplicate ownership.

---

# 2.10 Core Services

Every subsystem exposes a service interface.

```text
SessionService

PlannerService

WorkerService

IndexService

ToolService

GitService

TerminalService

ModelService

PromptService

MemoryService

ConfigurationService
```

Services communicate through interfaces, never concrete implementations.

---

# 2.11 Workspace Architecture

Every session runs inside a Workspace.

```text
Workspace

├── Source Code

├── .ailoom/

│   ├── index.db

│   ├── summaries/

│   ├── checkpoints/

│   ├── cache/

│   ├── logs/

│   └── session/

│

├── .git/

└── Project Files
```

`.ailoom/` is ignored by Git by default.

---

# 2.12 Execution State Machine

Every task follows the same lifecycle.

```text
Created

↓

Planning

↓

Queued

↓

Running

↓

Waiting Tool

↓

Running

↓

Completed
```

Possible failure transitions:

```text
Running

↓

Failed

↓

Retry

↓

Running
```

or

```text
Running

↓

Needs Human Approval
```

---

# 2.13 Event Flow

Example:

```text
User Prompt

↓

SessionCreated

↓

PlanningStarted

↓

FilesDiscovered

↓

PlanGenerated

↓

TaskQueued

↓

WorkerStarted

↓

ToolExecuted

↓

FileUpdated

↓

TestsStarted

↓

TestsPassed

↓

ReviewStarted

↓

Completed
```

Events are append-only.

No event is modified after emission.

---

# 2.14 Configuration Hierarchy

Configuration precedence:

```text
CLI Flags

↓

Workspace Config

↓

User Config

↓

System Defaults
```

Lower levels are overridden by higher levels.

---

# 2.15 Plugin Boundaries

Future extensibility points:

```text
Models

Tools

Indexers

Prompt Packs

Review Strategies

Language Support

Output Renderers

Permission Providers
```

Every plugin communicates through interfaces only.

---

# 2.16 Error Recovery Strategy

Every operation is recoverable.

```text
Tool Failure

↓

Retry

↓

Alternative Strategy

↓

Planner Decision

↓

User Approval

↓

Abort
```

Nothing crashes the session.

---

# 2.17 Architectural Constraints

1. Models never touch the filesystem directly.

2. Models never execute shell commands directly.

3. All external actions require tools.

4. Every file modification is tracked.

5. Every tool call is logged.

6. Every task is replayable.

7. Every session can be resumed.

8. Every component has a single responsibility.

9. Planner and workers are stateless outside the workflow state.

10. Infrastructure is replaceable without changing orchestration logic.

---

# 2.18 Final Architecture

```text
                    User
                      │
                 OpenCode
                      │
               OpenAI API Server
                      │
              Session Manager
                      │
                 Event Bus
                      │
              LangGraph Runtime
                      │
      ┌───────────────┴────────────────┐
      │                                │
 Planner                      Task Scheduler
      │                                │
      └───────────────┬────────────────┘
                      ▼
                   Workers
                      │
                Tool Executor
                      │
      ┌───────────────┼──────────────────────────┐
      ▼               ▼              ▼           ▼
Filesystem      Terminal        Git Service   Index Service
                                                    │
                                                    ▼
                                              SQLite Index
                                                    │
                                                    ▼
                                              Model Router
                                                    │
                                               LM Studio
                                                    │
                                        Planner / Worker Models
```

---
