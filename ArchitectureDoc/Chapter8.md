# AI Loom Architecture Specification

# Chapter 8 — Project Indexing Engine

**Version:** 1.0 Draft

---

# 8.1 Purpose

The Project Indexing Engine is responsible for transforming an arbitrary source code repository into a structured, queryable knowledge base.

The indexing engine is the foundation of AI Loom.

Without a good index:

* Context retrieval is poor.
* Planning becomes expensive.
* Workers receive incorrect context.
* Token usage explodes.

The indexing engine should answer most repository questions **without involving an LLM**.

---

# 8.2 Design Philosophy

The indexing engine follows three principles:

1. Parse once.
2. Query many.
3. Update incrementally.

A repository should almost never require a complete re-index.

---

# 8.3 Responsibilities

The indexing engine is responsible for:

* File discovery
* Language detection
* AST parsing
* Symbol extraction
* Dependency extraction
* Reference analysis
* Call graph construction
* Framework detection
* Project summarisation
* Incremental updates

It is **not** responsible for:

* Planning
* Prompt creation
* Model inference
* File editing

---

# 8.4 High-Level Pipeline

```text
Workspace

↓

Scanner

↓

Language Detector

↓

Tree-sitter Parser

↓

Symbol Extractor

↓

Reference Extractor

↓

Dependency Builder

↓

Summary Generator

↓

SQLite Database

↓

Context Engine
```

---

# 8.5 Initial Index Flow

When a workspace is opened:

```text
Workspace

↓

Validate

↓

Read Ignore Rules

↓

Discover Files

↓

Detect Languages

↓

Parse AST

↓

Extract Symbols

↓

Extract References

↓

Build Graph

↓

Generate Summaries

↓

Persist Database
```

Only after this is complete is the workspace considered "Ready".

---

# 8.6 File Discovery

The scanner walks the workspace.

Default exclusions:

```text
.git/

node_modules/

dist/

build/

target/

coverage/

.venv/

venv/

__pycache__/

.cache/

.next/

.nuxt/
```

User-defined exclusions are merged from:

* `.gitignore`
* `.ailoomignore`
* configuration

---

# 8.7 Language Detection

Language detection order:

1. File extension
2. Shebang
3. Tree-sitter parser validation
4. MIME fallback

Example:

```text
.py

↓

Python Parser
```

---

# 8.8 Supported Languages (V1)

Initial support:

```text
Python

TypeScript

JavaScript

Java

C#

Go

Rust

C++

C

JSON

YAML

Markdown

HTML

CSS

SQL
```

Adding a language should only require:

* Tree-sitter grammar
* Query definitions

---

# 8.9 Parsing Strategy

Each file is parsed independently.

```text
Source File

↓

Tree-sitter

↓

AST

↓

Visitors

↓

Domain Objects
```

Failures do not stop indexing.

---

# 8.10 Symbol Extraction

Extract:

```text
Functions

Methods

Classes

Enums

Interfaces

Modules

Variables

Constants

Namespaces

Decorators

Attributes
```

Each symbol receives a stable identifier.

---

# 8.11 Stable Symbol IDs

Never use line numbers.

Instead:

```text
workspace_hash

+

relative_path

+

symbol_path

+

signature_hash
```

Example:

```text
src/auth.py

↓

AuthService.login()

↓

HASH
```

This survives unrelated edits.

---

# 8.12 Symbol Paths

Examples:

```text
login()

UserService.login()

Auth.API.login()

Database.Connection.open()
```

Every symbol has a canonical path.

---

# 8.13 Reference Extraction

Every symbol usage is recorded.

Types include:

```text
Imports

Function Calls

Method Calls

Class Inheritance

Interface Implementation

Variable Reads

Variable Writes

Type References

Decorators

Annotations
```

---

# 8.14 Call Graph

Example:

```text
login()

↓

validate_user()

↓

get_user()

↓

database.query()
```

Stored separately from references.

Call graph supports:

* impact analysis
* context retrieval
* planning

---

# 8.15 Import Graph

Example:

```text
api.py

↓

service.py

↓

repository.py

↓

database.py
```

Useful for architectural reasoning.

---

# 8.16 Framework Detection

Automatically identify frameworks.

Examples:

Python

```text
FastAPI

Flask

Django

SQLAlchemy

Pydantic
```

TypeScript

```text
React

Next.js

NestJS

Express

Vue

Angular
```

Java

```text
Spring

Quarkus
```

Frameworks influence:

* planner
* prompts
* verification

---

# 8.17 Configuration Detection

Automatically detect:

```text
package.json

pyproject.toml

requirements.txt

Cargo.toml

pom.xml

build.gradle

Dockerfile

docker-compose.yml

tsconfig.json

vite.config.ts
```

Extract:

* package manager
* build commands
* formatter
* linter
* test framework

---

# 8.18 File Metadata

Each file stores:

```text
Path

Language

Hash

Size

Lines

Encoding

Last Indexed

Imports

Exports

Summary

Diagnostics
```

No source code is stored.

---

# 8.19 Region Indexing

Each file is divided into logical regions.

Example:

```text
auth.py

Imports

↓

Constants

↓

AuthService

↓

Helper Functions

↓

CLI
```

Each region becomes independently retrievable.

---

# 8.20 Summary Generation

Summaries are generated after parsing.

Levels:

```text
Project

Module

File

Class

Function
```

Generation is asynchronous.

The repository becomes usable before summaries complete.

---

# 8.21 Dependency Graph

The dependency graph combines:

```text
Imports

Calls

Inheritance

Composition

Configuration

Routes

Database Models
```

This graph becomes the planner's primary source of truth.

---

# 8.22 Semantic Tags

Each symbol receives tags.

Examples:

```text
Authentication

Database

API

Configuration

Frontend

CLI

Utility

Testing
```

Tags improve retrieval quality.

---

# 8.23 Route Detection

Framework-specific extractors identify endpoints.

Example:

```python
@app.post("/login")
```

Produces:

```text
POST /login

↓

login()

↓

AuthService
```

Useful for full-stack planning.

---

# 8.24 Test Mapping

Automatically associate tests.

Example:

```text
auth.py

↓

test_auth.py
```

Mapping methods:

* naming convention
* imports
* symbol references

Planner uses this during verification.

---

# 8.25 Git Integration

Index stores:

```text
Current Branch

HEAD Commit

Modified Files

Untracked Files

Deleted Files
```

Git information influences ranking.

---

# 8.26 File Watcher

Watch for:

```text
Create

Modify

Delete

Rename
```

Events enqueue incremental indexing jobs.

No polling.

Use native filesystem notifications where available.

---

# 8.27 Incremental Indexing

When a file changes:

```text
Modified File

↓

Parse

↓

Update Symbols

↓

Update References

↓

Update Call Graph

↓

Update Summary

↓

Invalidate Context Cache
```

Everything else remains untouched.

---

# 8.28 Delete Handling

Deleting a file:

```text
Delete File

↓

Remove Symbols

↓

Remove References

↓

Repair Graph

↓

Invalidate Cache
```

---

# 8.29 Rename Handling

Renames preserve identity where possible.

Procedure:

```text
Rename

↓

Compare AST

↓

Reuse Symbol IDs

↓

Update Paths

↓

Update References
```

This prevents unnecessary cache invalidation.

---

# 8.30 Database Schema

Core tables:

```text
projects

files

regions

symbols

references

call_graph

imports

summaries

embeddings

frameworks

configurations

git_state

diagnostics

index_jobs
```

Each table has a dedicated repository class.

---

# 8.31 Query API

The indexing engine exposes deterministic queries.

Examples:

```text
find_symbol()

find_callers()

find_callees()

find_routes()

find_tests()

find_imports()

find_dependents()

find_file()

find_region()

search_text()

search_semantic()
```

Neither planners nor workers access SQLite directly.

---

# 8.32 Performance Targets

Target performance on a typical developer machine:

| Repository Size | Initial Index |
| --------------- | ------------: |
| 1k files        |         < 5 s |
| 10k files       |        < 45 s |
| 50k files       |       < 4 min |

Incremental update:

Single file:

```text
< 200 ms
```

---

# 8.33 Error Handling

If parsing fails:

```text
Tree-sitter

↓

Diagnostic

↓

Best-Effort Metadata

↓

Continue Indexing
```

One broken file must never stop the workspace.

---

# 8.34 Extensibility

Every language adapter implements:

```python
class LanguageIndexer:
    detect()
    parse()
    extract_symbols()
    extract_references()
    extract_regions()
    detect_frameworks()
```

No language-specific logic exists elsewhere.

---

# 8.35 Background Jobs

Long-running tasks execute asynchronously.

Jobs include:

* Summary generation
* Embedding generation
* Repository statistics
* Framework confidence updates
* Dead code analysis (future)

The index remains available while jobs run.

---

# 8.36 Diagnostics

The index stores diagnostics separately from the compiler.

Examples:

```text
Syntax Errors

Unsupported Grammar

Encoding Errors

Large File Warning

Skipped File
```

Useful for debugging AI Loom itself.

---

# 8.37 Design Constraints

1. Never require an LLM for indexing.
2. Never store full source code in SQLite.
3. Every symbol must have a stable identifier.
4. Parsing must be deterministic.
5. Incremental indexing must be the default.
6. Broken files must not stop indexing.
7. Indexing must be language-agnostic.
8. Query latency should be independent of repository size wherever practical.
9. File watcher events must be debounced to avoid repeated re-indexing during rapid saves.
10. The index is the single source of truth for repository structure.

---

# Architect's Notes (Normative)

## 1. Separate Structure from Semantics

Maintain two distinct layers:

**Structural Index**

* AST
* Symbols
* References
* Call graph
* Imports

**Semantic Index**

* Summaries
* Embeddings
* Tags
* Architectural descriptions

The structural index should always be authoritative. Semantic data enhances retrieval but must never override structural facts.

---

## 2. Never Reparse Unchanged Files

Each file should be identified by a content hash (e.g. SHA-256 or BLAKE3).

If the hash is unchanged:

```text
Skip Parsing

↓

Reuse Existing Index
```

This dramatically reduces startup time.

---

## 3. Build for Millions of Symbols

Even though Version 1 targets local projects, the schema should scale to repositories with millions of symbols.

Avoid loading entire tables into memory.

All queries should be indexed and paginated where appropriate.

---

## 4. Prefer Graph Traversal over Search

When asked:

> "Modify login"

The ideal flow is:

```text
Find Symbol

↓

Traverse Graph

↓

Find Related Regions

↓

Retrieve Code
```

Not:

```text
grep "login"
```

Text search is a fallback, not the primary mechanism.

---

## 5. Future-Proof the Index

The indexing engine should become the foundation for future capabilities such as:

* Dead code detection
* Architectural visualisation
* Dependency impact analysis
* Automatic documentation
* Code ownership inference
* Security auditing
* Performance hotspot detection

For this reason, the index should be treated as a long-lived knowledge graph rather than a temporary cache.

---