# AI Loom Architecture Specification

# Chapter 10 — Tool Execution Engine

**Version:** 1.0 Draft

---

# 10.1 Purpose

The Tool Execution Engine is the only subsystem allowed to interact with the outside world.

Everything that affects the workspace must pass through this engine.

This includes:

* Reading files
* Writing files
* Running shell commands
* Git operations
* Package installation
* Network access
* Future browser automation

Neither the Planner nor the Worker may directly access the operating system.

---

# 10.2 Philosophy

The Tool Engine follows three principles:

1. Validate before execution.
2. Execute deterministically.
3. Record everything.

Every external action must be:

* authorised
* validated
* logged
* reproducible

---

# 10.3 Responsibilities

The Tool Engine is responsible for:

* Tool execution
* Permission enforcement
* Workspace isolation
* Result collection
* Timeout handling
* Cancellation
* Logging
* Error translation
* Rollback metadata

It is **not** responsible for:

* Planning
* Reasoning
* Prompting
* Context generation

---

# 10.4 High-Level Architecture

```text
Worker

↓

Tool Request

↓

Permission Manager

↓

Argument Validator

↓

Tool Dispatcher

↓

Tool Adapter

↓

Operating System

↓

Result Collector

↓

Worker
```

---

# 10.5 Tool Request

Every tool call is represented as:

```text
ToolRequest

id

tool

arguments

workspace

task_id

timeout

permission_level
```

Workers never execute Python directly.

---

# 10.6 Tool Result

Every execution returns:

```text
ToolResult

status

stdout

stderr

exit_code

files_changed

execution_time

diagnostics
```

Even failures produce a ToolResult.

---

# 10.7 Tool Categories

Version 1 supports:

Filesystem

```text
read_file

write_file

patch_file

delete_file

move_file

list_directory

create_directory
```

Terminal

```text
run_command
```

Git

```text
git_status

git_diff

git_branch

git_commit
```

Search

```text
find_symbol

find_file

find_text
```

Workspace

```text
workspace_info
```

Future:

* Browser
* Docker
* Kubernetes
* SSH
* Database
* Cloud providers

---

# 10.8 Filesystem Sandbox

Every session has a workspace root.

Example:

```text
/home/sid/projects/demo
```

Allowed:

```text
/home/sid/projects/demo/src
```

Denied:

```text
/etc/

/home/sid/.ssh

/home/sid/Documents
```

unless explicitly permitted.

All paths are canonicalised before validation.

---

# 10.9 Path Validation

Validation steps:

```text
Input Path

↓

Resolve Symlinks

↓

Normalise

↓

Canonical Path

↓

Inside Workspace?

↓

Execute
```

Path traversal (`../`) must never escape the workspace.

---

# 10.10 Read File

Input:

```text
path
```

Output:

```text
Content

Encoding

Hash

Metadata
```

Reads are cached when safe.

---

# 10.11 Write File

Input:

```text
Path

Content

Expected Hash
```

Algorithm:

```text
Verify Hash

↓

Write Temp File

↓

Atomic Rename

↓

Update Metadata
```

Atomic writes prevent partial corruption.

---

# 10.12 Patch File

Preferred editing mechanism.

Input:

```text
Path

Patch
```

Algorithm:

```text
Read

↓

Verify

↓

Apply

↓

Validate

↓

Write
```

If patch application fails, return a structured error.

---

# 10.13 Delete File

Delete requests require:

* path validation
* permission check
* optional user approval

Deleted files may first be moved to a temporary recovery location (configurable) before permanent removal.

---

# 10.14 Directory Operations

Supported:

```text
Create

Delete Empty

List

Exists
```

Recursive deletion requires explicit approval.

---

# 10.15 Terminal Execution

Worker requests:

```text
Run Tests
```

Tool Engine executes:

```text
pytest
```

Execution flow:

```text
Validate

↓

Spawn Process

↓

Capture Output

↓

Monitor Timeout

↓

Return Result
```

---

# 10.16 Process Isolation

Each command runs:

* in the workspace
* with a controlled environment
* without inheriting arbitrary user shell configuration (configurable)

The working directory is always explicit.

---

# 10.17 Timeouts

Every command has:

```text
Soft Timeout

Hard Timeout
```

Example:

```text
Soft

30 s

Hard

60 s
```

Soft timeout:

* notify worker

Hard timeout:

* terminate process

---

# 10.18 Streaming Output

Long-running commands stream:

```text
stdout

stderr
```

back to the Worker.

Example:

```text
Running Tests...

Test 1 PASS

Test 2 PASS

Test 3 FAIL
```

Worker does not wait until completion to observe progress.

---

# 10.19 Cancellation

If cancellation requested:

```text
Worker

↓

Tool Engine

↓

SIGTERM

↓

Grace Period

↓

SIGKILL
```

Platform-specific equivalents should be used where necessary.

---

# 10.20 Git Tools

Supported:

```text
Status

Diff

Current Branch

Commit

Log (limited)
```

Git operations are read-only by default.

Mutating operations require explicit permission.

---

# 10.21 Package Installation

Commands like:

```text
pip install

npm install

cargo add
```

are classified as **high-risk**.

Default behaviour:

```text
ASK USER
```

Planner may recommend installation, but the Tool Engine enforces approval.

---

# 10.22 Network Access

Network access is disabled by default.

Allowed examples:

* Download dependency
* Fetch documentation
* MCP server
* API requests

Blocked unless policy allows.

---

# 10.23 Environment Variables

Workers never receive the host environment.

Instead:

```text
Allowed Variables

↓

Filtered Environment

↓

Tool
```

Sensitive variables are never exposed unless explicitly whitelisted.

Examples:

```text
PATH

HOME

TMPDIR
```

Secrets should be injected only when required.

---

# 10.24 Tool Registry

Each tool implements:

```python
class Tool:
    name()
    validate()
    execute()
    cancel()
    capabilities()
```

Registration is automatic.

The dispatcher never contains tool-specific logic.

---

# 10.25 Error Classification

Tool errors are standardised.

Categories:

```text
ValidationError

PermissionError

TimeoutError

ToolFailure

NotFound

Conflict

IOError

InternalError
```

Workers receive structured errors instead of raw exceptions.

---

# 10.26 Retry Policy

Safe operations may retry automatically.

Examples:

Retry:

* temporary file lock
* transient process startup failure

Do not retry automatically:

* permission denied
* invalid path
* malformed patch

---

# 10.27 Audit Log

Every tool invocation records:

```text
Timestamp

Worker

Task

Tool

Arguments (sanitised)

Duration

Status

Files Changed

Exit Code
```

Logs are append-only.

---

# 10.28 Tool Permissions

Each tool belongs to one permission level.

| Level     | Examples                                      |
| --------- | --------------------------------------------- |
| Safe      | Read file, list directory                     |
| Moderate  | Write file, patch file                        |
| Elevated  | Delete file, install packages                 |
| Dangerous | Recursive delete, unrestricted shell, network |

The Permission Manager decides whether to:

* allow
* ask
* deny

---

# 10.29 Rollback Metadata

Every mutating operation stores:

```text
Original Hash

New Hash

Timestamp

Task

Worker
```

This enables future undo functionality.

---

# 10.30 Observability

Every tool emits structured events.

Example:

```text
ToolRequested

↓

ValidationPassed

↓

ExecutionStarted

↓

ExecutionCompleted

↓

ResultReturned
```

These events power:

* progress UI
* debugging
* analytics

---

# 10.31 Extending the Tool Engine

Adding a new tool requires:

1. Implement `Tool` interface.
2. Register tool.
3. Define permission level.
4. Add validation rules.
5. Add tests.

No Worker or Planner changes should be necessary.

---

# 10.32 Design Constraints

1. All external actions go through the Tool Engine.
2. Every tool validates its inputs.
3. Every path is canonicalised before use.
4. Every mutating operation is logged.
5. Every tool is cancellable where practical.
6. Tool outputs are structured and deterministic.
7. The Tool Engine enforces permissions; workers cannot bypass them.
8. Workspace isolation is mandatory.
9. Tool failures never crash the execution engine.
10. Every tool invocation is auditable.

---

# Architect's Notes (Normative)

## 1. Build Tools as Independent Plugins

Each tool should live in its own module.

Example:

```text
tools/
├── filesystem/
├── terminal/
├── git/
├── search/
├── workspace/
└── registry.py
```

The dispatcher loads tools dynamically.

---

## 2. Prefer AST-Based Editing

Where supported, implement an AST editing tool in addition to text patching.

Example:

```text
replace_function()

rename_symbol()

insert_import()

remove_unused_import()
```

AST edits are safer than text replacements and preserve formatting more reliably.

---

## 3. Restrict Shell Usage

Avoid using the shell when a dedicated tool exists.

Prefer:

```text
find_symbol()
```

over:

```bash
grep -R "symbol"
```

Prefer:

```text
patch_file()
```

over:

```bash
sed -i
```

Dedicated tools are more reliable, portable and auditable.

---

## 4. Add Dry-Run Support

Every mutating tool should optionally support:

```text
dry_run = true
```

This returns:

* intended changes
* affected files
* validation results

without modifying the workspace.

Useful for previews, reviews and future approval workflows.

---

## 5. Make Tool Results Machine-Friendly

Avoid forcing the Worker to parse human-readable text.

Prefer:

```json
{
  "status": "success",
  "files_changed": [
    "src/auth.py"
  ],
  "exit_code": 0
}
```

over free-form console output whenever possible.

Structured results reduce hallucinations and simplify orchestration.

---