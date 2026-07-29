# AI Loom Architecture Specification

# Chapter 15 — Plugin System & Extensibility

**Version:** 1.0 Draft

---

# 15.1 Purpose

The Plugin System allows AI Loom to evolve without modifying its core.

Everything that isn't fundamental should eventually become a plugin.

Examples include:

* New LLM providers
* Programming languages
* Framework support
* Tool integrations
* Context retrievers
* Memory providers
* UI extensions
* Planning strategies

The core should remain small, stable and highly testable.

---

# 15.2 Philosophy

The plugin system follows one rule:

> **Open for extension, closed for modification.**

Adding functionality should never require editing the orchestrator.

---

# 15.3 Plugin Architecture

```text
                 AI Loom Core
                       │
      ┌────────────────┼─────────────────┐
      ▼                ▼                 ▼
 Language Plugins  Tool Plugins   Provider Plugins
      │                │                 │
      ▼                ▼                 ▼
 Framework Plugins  UI Plugins   Planner Plugins
```

The core only understands interfaces.

---

# 15.4 Core vs Plugins

Core responsibilities:

* Session Manager
* Planner
* Worker
* Context Engine
* Tool Dispatcher
* Permission System
* Event Bus

Plugins provide:

* New capabilities
* Integrations
* Domain knowledge

---

# 15.5 Plugin Types

Version 1 supports:

```text
Language

Framework

Provider

Tool

Prompt

Planner

Reviewer

Memory

UI

Workflow
```

Future plugin types may be added without changing existing ones.

---

# 15.6 Plugin Manifest

Every plugin includes a manifest.

```yaml
id: python-language

name: Python Support

version: 1.0.0

author: AI Loom

type: language

entrypoint: python_plugin.py

api_version: 1

dependencies:
  - tree-sitter-python
```

The manifest is loaded before execution.

---

# 15.7 Plugin Lifecycle

```text
Discover

↓

Validate

↓

Load

↓

Initialize

↓

Register

↓

Active

↓

Unload
```

Failed plugins never prevent startup.

---

# 15.8 Discovery

Default locations:

```text
plugins/

~/.ailoom/plugins/

workspace/.ailoom/plugins/
```

Additional directories may be configured.

---

# 15.9 Plugin Registration

Each plugin registers its capabilities.

Example:

```python
register_language(
    PythonLanguagePlugin()
)
```

Core components interact only with the registry.

---

# 15.10 Language Plugins

A language plugin provides:

```python
class LanguagePlugin:

    detect()

    parse()

    symbols()

    references()

    regions()

    formatter()

    diagnostics()
```

Tree-sitter integration belongs here.

---

# 15.11 Framework Plugins

Framework plugins detect and enrich repository understanding.

Examples:

```text
FastAPI

React

Next.js

Spring

Django

Vue
```

Responsibilities:

* Route detection
* Project conventions
* Special retrieval rules
* Framework-specific summaries

---

# 15.12 Tool Plugins

Every tool is itself a plugin.

Examples:

```text
Filesystem

Git

Docker

Browser

Database

SSH

Kubernetes
```

Tool plugins declare:

* capabilities
* permissions
* supported platforms

---

# 15.13 Provider Plugins

Provider plugins expose LLMs.

Example interface:

```python
class ProviderPlugin:

    chat()

    stream()

    embeddings()

    health()

    list_models()
```

Examples:

* LM Studio
* Ollama
* OpenAI-compatible
* Gemini
* Anthropic

---

# 15.14 Planner Plugins

Planning strategies should be replaceable.

Examples:

```text
Hierarchical Planner

Research Planner

Bugfix Planner

Refactor Planner

Documentation Planner
```

Users may switch planners without changing Workers.

---

# 15.15 Reviewer Plugins

Reviewers validate completed work.

Examples:

```text
Security Reviewer

Style Reviewer

Performance Reviewer

Accessibility Reviewer

Architecture Reviewer
```

Multiple reviewers may run sequentially.

---

# 15.16 Prompt Plugins

Prompt generation should be modular.

Examples:

```text
Python Worker Prompt

React Worker Prompt

Rust Worker Prompt

Security Audit Prompt
```

Prompt logic should not be hardcoded.

---

# 15.17 Memory Plugins

Alternative memory implementations.

Examples:

```text
SQLite

PostgreSQL

Redis

Vector Store

Read-only Cache
```

The rest of AI Loom uses a common interface.

---

# 15.18 Workflow Plugins

Users may define custom workflows.

Example:

```text
Plan

↓

Implement

↓

Run Tests

↓

Run Linter

↓

Commit

↓

Create PR
```

Another workflow:

```text
Security Scan

↓

Dependency Update

↓

Regression Tests
```

---

# 15.19 UI Plugins

Possible future examples:

```text
VS Code

OpenCode

Terminal

Web Dashboard

JetBrains
```

Core logic should remain UI-independent.

---

# 15.20 Plugin Capabilities

Plugins advertise capabilities.

Example:

```yaml
capabilities:

  syntax_highlighting

  ast_parsing

  formatting

  diagnostics
```

The core never assumes optional functionality exists.

---

# 15.21 Dependencies

Plugins may depend on others.

Example:

```text
React Plugin

↓

TypeScript Plugin

↓

Tree-sitter TypeScript
```

Dependency resolution occurs before loading.

Circular dependencies are rejected.

---

# 15.22 Version Compatibility

Manifest includes:

```yaml
api_version: 1
```

Major API changes require new versions.

Old plugins should fail gracefully with clear diagnostics.

---

# 15.23 Isolation

A failing plugin:

```text
Throws Exception

↓

Unload Plugin

↓

Log Error

↓

Continue Startup
```

One broken plugin must never crash AI Loom.

---

# 15.24 Security

Plugin permissions:

```text
Filesystem

Network

Shell

Models

Memory

Events
```

Plugins receive only the capabilities they request and are granted.

---

# 15.25 Event Integration

Plugins may subscribe to events.

Example:

```text
TaskCompleted

↓

Security Plugin

↓

Run Static Analysis
```

Loose coupling is preferred.

---

# 15.26 Configuration

Each plugin has its own configuration.

Example:

```yaml
plugins:

  python:

    formatter: black

  react:

    use_server_components: true
```

Configurations are namespaced.

---

# 15.27 Hot Reload

Development mode supports:

```text
Plugin Changed

↓

Unload

↓

Reload

↓

Re-register
```

No application restart required.

---

# 15.28 Plugin API

Every plugin implements:

```python
class Plugin:

    metadata()

    initialize()

    shutdown()

    health()

    capabilities()
```

Optional interfaces extend functionality.

---

# 15.29 Testing

Every plugin should include:

* Unit tests
* Integration tests
* Compatibility tests

Reference implementations should be provided.

---

# 15.30 Distribution

Plugins may be installed from:

```text
Local Directory

Git Repository

Plugin Registry (future)
```

Installation is explicit.

Automatic downloads are disabled by default.

---

# 15.31 Design Constraints

1. Core never depends on optional plugins.
2. Plugins communicate through defined interfaces.
3. Plugin failures are isolated.
4. Capabilities are explicitly declared.
5. API versions are enforced.
6. Configuration is namespaced.
7. Plugins are discoverable.
8. Hot reload is optional.
9. Plugins never bypass the Permission Manager.
10. Plugins are first-class citizens.

---

# Architect's Notes (Normative)

## 1. Make Everything Replaceable

A useful rule:

If a component might reasonably have multiple implementations, define an interface.

Examples:

* Planner
* Worker Prompt Builder
* Provider
* Indexer
* Search Strategy
* Memory Store
* Reviewer

This prevents architectural lock-in.

---

## 2. Build an Internal Service Registry

Instead of plugins directly referencing each other:

```text
Plugin

↓

Service Registry

↓

Requested Service
```

This reduces coupling and simplifies dependency management.

---

## 3. Support Capability Negotiation

Instead of checking plugin names:

Bad:

```python
if plugin.name == "FastAPI":
```

Good:

```python
if plugin.supports("route_detection"):
```

Capabilities scale far better than hardcoded identities.

---

## 4. Separate Stable APIs from Experimental APIs

Maintain two namespaces.

```text
api/

experimental/
```

Plugins using experimental APIs accept the risk of breaking changes.

Core APIs should prioritise long-term stability.

---

## 5. Design for an Ecosystem

Long-term, AI Loom should be more than a coding agent.

It should become a platform.

A healthy plugin ecosystem could include:

* Language packs
* Enterprise integrations
* Custom planners
* Security scanners
* Documentation generators
* CI/CD integrations
* Code quality analysers
* Company-specific coding standards
* Internal MCP connectors

The architecture should make external contributions feel natural rather than requiring modifications to the core.

---