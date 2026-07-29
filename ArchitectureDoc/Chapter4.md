# AI Loom Architecture Specification

# Chapter 4 — Core Domain Model & Data Structures

**Version:** 1.0 Draft

---

# 4.1 Purpose

This chapter defines the core objects used throughout AI Loom.

These are **domain objects**, not database models.

Every subsystem communicates using these structures.

No subsystem should pass raw JSON, dictionaries, or framework-specific objects internally.

---

# 4.2 Design Principles

Every domain object must satisfy:

* Immutable where possible
* Serializable
* Framework-independent
* Versionable
* Self-validating
* Single responsibility

All objects should be implemented as Python dataclasses or Pydantic models (v2), depending on validation requirements.

---

# 4.3 System Overview

The core domain consists of:

```text
Session
│
├── Workspace
├── Conversation
├── TaskGraph
├── Memory
├── Permissions
└── EventLog

TaskGraph
│
├── Task
├── WorkerAssignment
├── Dependency
└── Review

Project
│
├── File
├── Symbol
├── Reference
├── Summary
└── Embedding
```

---

# 4.4 Session

A Session represents one interaction with AI Loom.

It owns the complete execution state.

Fields:

```text
Session
--------
id
created_at
updated_at

workspace

conversation

task_graph

memory

permissions

configuration

status

logs

checkpoints
```

Rules:

* Every request belongs to exactly one session.
* Sessions are resumable.
* Sessions are isolated.
* Sessions never share mutable state.

---

# 4.5 Session Status

```text
CREATED

PLANNING

RUNNING

WAITING_TOOL

WAITING_USER

VERIFYING

COMPLETED

FAILED

CANCELLED
```

Only one status may exist at a time.

---

# 4.6 Workspace

Represents a project directory.

Fields:

```text
Workspace

id

root_path

git_enabled

language

framework

package_manager

index_version

created

last_scan

statistics
```

Statistics include:

* files
* symbols
* languages
* size
* git branch

---

# 4.7 Conversation

Stores only user-visible messages.

Planner reasoning is NOT stored here.

```text
Conversation

messages[]

token_count

compressed

summary
```

Messages:

```text
role

content

timestamp

attachments

metadata
```

---

# 4.8 Memory

Memory is generated.

Never manually edited.

Contains:

```text
Project Summary

Relevant Files

Relevant Symbols

Recent Changes

Current Objective

Coding Standards
```

Workers receive Memory, not Conversation.

---

# 4.9 Task Graph

Represents the execution DAG.

```text
TaskGraph

id

tasks

edges

root

status

statistics
```

Graph constraints:

* Directed
* Acyclic
* Connected
* Single root

---

# 4.10 Task

Most important object.

```text
Task

id

title

description

objective

inputs

outputs

constraints

priority

estimated_complexity

worker_type

required_symbols

required_files

status

result

retries

parent

children
```

Workers execute Tasks.

Never Conversations.

---

# 4.11 Task Status

```text
CREATED

READY

RUNNING

WAITING_TOOL

WAITING_REVIEW

FAILED

RETRYING

BLOCKED

COMPLETED
```

---

# 4.12 Dependency Edge

```text
Dependency

from_task

to_task

reason
```

Example:

```text
Create Database

↓

Implement API
```

API depends on Database.

---

# 4.13 Worker Assignment

```text
WorkerAssignment

worker_id

worker_type

model

temperature

max_tokens

context_budget

tools
```

Created by Scheduler.

---

# 4.14 Worker Result

```text
WorkerResult

task_id

status

tool_calls

modified_files

summary

token_usage

execution_time

errors
```

Planner receives WorkerResult.

---

# 4.15 Tool Call

All external actions become ToolCalls.

```text
ToolCall

id

tool

arguments

request_time

status

duration

result
```

Workers never call Python directly.

---

# 4.16 Tool Result

```text
ToolResult

success

stdout

stderr

files_changed

metadata

execution_time
```

Returned to worker.

---

# 4.17 Project

Represents indexed repository.

```text
Project

workspace

languages

frameworks

symbols

files

dependencies

summaries
```

Only one Project per Workspace.

---

# 4.18 File

Metadata only.

```text
ProjectFile

path

language

hash

size

lines

imports

exports

summary

last_indexed

embedding
```

No source code stored.

---

# 4.19 Symbol

```text
Symbol

id

name

kind

signature

file

start_line

end_line

parent

visibility

documentation
```

Kinds:

```text
FUNCTION

CLASS

METHOD

VARIABLE

ENUM

INTERFACE

MODULE

TYPE
```

---

# 4.20 Reference

Represents symbol usage.

```text
Reference

symbol

file

line

type
```

Types:

```text
IMPORT

CALL

INHERITANCE

ASSIGNMENT

RETURN

PARAMETER
```

---

# 4.21 Summary

AI-generated metadata.

```text
Summary

target

type

text

tokens

created

version
```

Types:

* File
* Class
* Function
* Module
* Project

---

# 4.22 Embedding

```text
Embedding

target

vector

model

dimension

created
```

Embeddings are optional.

They are regenerated independently.

---

# 4.23 Planner Output

Planner returns:

```text
Plan

objective

reasoning_summary

tasks

dependencies

verification_plan

estimated_duration
```

Internal reasoning is never persisted verbatim.

---

# 4.24 Review

Represents planner verification.

```text
Review

task

score

issues

recommendations

approved
```

Scores:

0–100

Below threshold:

Retry.

---

# 4.25 Execution Report

Returned to user.

```text
ExecutionReport

tasks_completed

files_modified

tests_run

tests_passed

commands

warnings

summary
```

---

# 4.26 Configuration

```text
Configuration

models

permissions

timeouts

tools

prompts

logging

workspace
```

Immutable during execution.

---

# 4.27 Permission Policy

```text
PermissionPolicy

filesystem

terminal

network

git

packages
```

Each field:

```text
ALLOW

ASK

DENY
```

---

# 4.28 Event

Everything important becomes an event.

```text
Event

id

timestamp

type

source

payload

session
```

Events are append-only.

---

# 4.29 Checkpoint

Allows recovery.

```text
Checkpoint

id

graph_state

memory

task_status

files

timestamp
```

Planner can resume from checkpoints.

---

# 4.30 Terminal Command

```text
Command

id

command

cwd

environment

timeout

permission

status
```

Executed only by Tool Executor.

---

# 4.31 Git Change

```text
GitChange

path

change_type

before_hash

after_hash
```

Types:

* Added
* Modified
* Deleted
* Renamed

---

# 4.32 Context Package

Workers never receive arbitrary prompts.

Instead they receive:

```text
ContextPackage

objective

task

project_summary

relevant_files

relevant_symbols

recent_changes

constraints

style_guide

tool_manifest
```

This is the only context passed to the model.

---

# 4.33 Metrics

Every execution records:

```text
ExecutionMetrics

tokens

prompt_tokens

completion_tokens

tool_calls

latency

model_time

tool_time

planning_time

review_time
```

Useful for benchmarking.

---

# 4.34 Object Relationships

```text
Session
│
├── Workspace
├── Conversation
├── Memory
├── TaskGraph
│      │
│      ├── Task
│      ├── Dependency
│      └── WorkerAssignment
│
├── Configuration
└── PermissionPolicy

Project
│
├── File
├── Symbol
├── Reference
├── Summary
└── Embedding

Worker
│
├── ContextPackage
├── ToolCall
└── WorkerResult

Planner
│
├── Plan
├── Review
└── ExecutionReport
```

---

# 4.35 Invariants

The following rules must always hold:

1. Every Task belongs to exactly one TaskGraph.
2. Every Task has exactly one status.
3. Every Session owns exactly one Workspace.
4. Every Symbol belongs to one File.
5. Every Reference points to an existing Symbol.
6. Every ToolCall produces exactly one ToolResult.
7. Every WorkerResult belongs to one Task.
8. Every Checkpoint belongs to one Session.
9. Every ContextPackage is immutable once created.
10. Every Event is append-only and never edited.

These invariants define the contract that every subsystem must respect.

---
