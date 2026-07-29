# AI Loom Architecture Specification

# Chapter 16 — Deployment, Configuration & Runtime

**Version:** 1.0 Draft

---

# 16.1 Purpose

The Runtime is responsible for turning all AI Loom components into a single, coherent application.

It manages:

* Startup
* Shutdown
* Configuration
* Dependency injection
* Service lifecycle
* Runtime state
* Workspace sessions

The Runtime is the operating system of AI Loom.

---

# 16.2 Philosophy

The Runtime should:

* Start quickly
* Be deterministic
* Be configurable
* Be recoverable
* Be observable

A fresh startup should always produce the same runtime state given the same configuration.

---

# 16.3 Runtime Architecture

```text
                 AI Loom Runtime
                       │
     ┌─────────────────┼─────────────────┐
     ▼                 ▼                 ▼
 Service Registry   Config Loader   Session Manager
     │                 │                 │
     ▼                 ▼                 ▼
 Planner        Model Router      Tool Engine
     │                 │                 │
     ▼                 ▼                 ▼
 Context Engine   Memory System    Index Engine
```

Every subsystem is managed by the Runtime.

---

# 16.4 Startup Sequence

```text
Load Configuration

↓

Initialise Logger

↓

Load Plugins

↓

Create Service Registry

↓

Initialise Providers

↓

Start Event Bus

↓

Start Memory

↓

Start Index Engine

↓

Start Tool Engine

↓

Ready
```

No user session starts before all required services are healthy.

---

# 16.5 Shutdown Sequence

```text
Stop Sessions

↓

Finish Running Tasks

↓

Flush Events

↓

Persist Memory

↓

Close Providers

↓

Shutdown Plugins

↓

Exit
```

Graceful shutdown is always preferred.

---

# 16.6 Service Registry

Every core component is registered.

Example:

```text
Planner

WorkerFactory

ContextEngine

ToolDispatcher

IndexEngine

ModelRouter

MemoryStore

PermissionManager
```

Components never instantiate each other directly.

---

# 16.7 Dependency Injection

Services receive dependencies via constructors.

Example:

```python
class Planner:

    def __init__(
        self,
        context_engine,
        model_router,
        memory,
        events
    ):
        ...
```

Avoid global singletons wherever possible.

---

# 16.8 Configuration Sources

Configuration is merged from:

```text
Defaults

↓

Global Config

↓

User Config

↓

Workspace Config

↓

Environment Variables

↓

CLI Overrides
```

Later layers override earlier ones.

---

# 16.9 Configuration Files

Recommended locations:

```text
/etc/ailoom/

~/.config/ailoom/

workspace/.ailoom/
```

Workspace settings override global settings.

---

# 16.10 Configuration Structure

Example:

```yaml
runtime:

  workspace:

    auto_index: true

models:

  planner:

    profile: planner

permissions:

  network: ask

index:

  watch: true
```

Configuration should be hierarchical.

---

# 16.11 Profiles

Profiles group related settings.

Examples:

```text
Development

Review

CI

Offline

Performance
```

Users switch profiles instead of editing dozens of settings.

---

# 16.12 Environment Variables

Examples:

```text
AILOOM_HOME

AILOOM_CONFIG

AILOOM_WORKSPACE

AILOOM_LOG_LEVEL
```

Environment variables are optional.

---

# 16.13 Workspace Sessions

Each opened repository creates a session.

```text
Workspace

↓

Session

↓

Planner

↓

Workers

↓

Completion
```

Multiple workspaces may run simultaneously.

---

# 16.14 Session State

Stores:

```text
Workspace

Current Goal

Task Graph

Running Workers

Configuration

Permissions
```

Independent between sessions.

---

# 16.15 Workspace Metadata

Each workspace stores:

```text
Project ID

Last Index

Framework

Language

Planner State

Configuration

Memory Version
```

Metadata survives restarts.

---

# 16.16 Runtime Modes

Supported modes:

```text
Interactive

Daemon

Batch

CI

Read-only
```

Each mode adjusts behaviour.

---

# 16.17 Interactive Mode

Default mode.

Features:

* Live planning
* Streaming
* Progress updates
* Incremental indexing
* User approvals

---

# 16.18 Daemon Mode

Background service.

Supports:

* API
* Multiple clients
* Long-lived indexes
* Shared model pool

Useful for IDE integrations.

---

# 16.19 Batch Mode

Example:

```bash
ailoom run "Implement JWT authentication"
```

Executes task.

Returns result.

Exits.

---

# 16.20 CI Mode

Characteristics:

* Read-only by default
* Non-interactive
* Deterministic
* Approval disabled
* Machine-readable output

Useful for automated code review.

---

# 16.21 Read-Only Mode

Allowed:

* Indexing
* Planning
* Review
* Documentation

Denied:

* File edits
* Shell execution
* Package installation

---

# 16.22 Health Checks

Every service exposes:

```python
health()

↓

Healthy

Degraded

Unavailable
```

Runtime continuously monitors service health.

---

# 16.23 Failure Recovery

If a service fails:

```text
Restart

↓

Fallback

↓

Disable

↓

Notify User
```

Example:

Model provider offline.

Planner waits.

Tool Engine continues operating.

---

# 16.24 Crash Recovery

On unexpected termination:

```text
Session Checkpoint

↓

Restart

↓

Restore State

↓

Resume
```

Recovery is optional per workspace.

---

# 16.25 Configuration Reload

Supported for:

* Logging
* Routing policy
* Permissions
* Profiles

Some changes require service restart.

---

# 16.26 Runtime Metrics

Track:

```text
Startup Time

Memory Usage

CPU Usage

Model Count

Session Count

Index Size

Event Rate
```

Useful for optimisation.

---

# 16.27 Resource Management

The Runtime manages:

* Thread pools
* Async event loops
* Model loading
* Database connections
* File watchers

Ownership is centralised.

---

# 16.28 Concurrency

Recommended execution model:

```text
Planner

↓

Async Task Queue

↓

Workers

↓

Tool Engine
```

Avoid unnecessary threads.

Prefer asynchronous I/O where appropriate.

---

# 16.29 API Layer

Future runtime should expose:

```text
CLI

REST API

WebSocket

MCP Server

Python SDK
```

All APIs use the same internal services.

---

# 16.30 Packaging

Recommended distribution:

```text
Python Package

Standalone Binary

Docker Image

Development Source
```

Core behaviour remains identical.

---

# 16.31 Runtime Layout

```text
ailoom/

├── core/
├── planner/
├── worker/
├── routing/
├── tools/
├── context/
├── memory/
├── runtime/
├── plugins/
├── api/
├── cli/
├── config/
└── tests/
```

Clear boundaries are preferred over deeply nested packages.

---

# 16.32 Design Constraints

1. Runtime owns service lifecycle.
2. Configuration is layered and deterministic.
3. Sessions are isolated.
4. Services are dependency-injected.
5. Startup failures are explicit.
6. Runtime modes are configurable.
7. Configuration reload is safe.
8. Health checks are mandatory.
9. Crash recovery is optional but supported.
10. Runtime behaviour is reproducible.

---

# Architect's Notes (Normative)

## 1. Build AI Loom as a Long-Running Service

Although the CLI should be the primary interface initially, architect the runtime as if it will eventually become a daemon.

This enables:

* Multiple IDE clients
* Shared indexes
* Shared model pools
* Faster startup
* Remote execution

The CLI becomes a thin client over the runtime.

---

## 2. Separate Configuration from Code

Avoid hardcoded values.

Instead of:

```python
planner_model = "qwen3.6"
```

Use:

```yaml
models:

  planner:

    profile: planner
```

Configuration should control behaviour without requiring code changes.

---

## 3. Use a Service Container

Every service should be resolved through the Service Registry.

Avoid:

```python
planner = Planner()
```

Prefer:

```python
planner = services.resolve(Planner)
```

This greatly simplifies testing, plugin integration and future dependency injection.

---

## 4. Prefer Async Throughout the Runtime

Most operations are I/O bound:

* Reading files
* Running models
* Executing tools
* Database access
* Streaming responses

Using asynchronous APIs consistently will improve responsiveness and simplify concurrent worker execution later.

---

## 5. Prepare for AI Loom v2

The Runtime should be designed so that replacing local services with remote ones requires minimal changes.

For example:

```text
Current

Planner

↓

Local Worker

↓

Local Tool Engine

Future

Planner

↓

Remote Worker

↓

Remote Tool Engine
```

The orchestration APIs should remain unchanged.

This separation will allow AI Loom to evolve from a local coding assistant into a distributed AI engineering platform without major architectural redesign.

---
