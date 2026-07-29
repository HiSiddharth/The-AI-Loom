# AI Loom Architecture Specification

# Chapter 13 — Safety, Permissions & Sandboxing

**Version:** 1.0 Draft

---

# 13.1 Purpose

The Safety System ensures that AI Loom can operate autonomously **without becoming dangerous**.

Unlike a normal coding assistant, AI Loom has permission to:

* modify files
* execute commands
* install packages
* interact with Git

Therefore, every action must be governed by explicit security policies.

The Safety System guarantees:

* Workspace isolation
* Principle of least privilege
* Explicit user consent for risky actions
* Deterministic permission enforcement
* Complete auditability

---

# 13.2 Design Philosophy

Every action should answer three questions:

```text
Is it allowed?

Should it require approval?

Can it be safely reversed?
```

If any answer is uncertain:

> Ask the user.

---

# 13.3 Security Layers

```text
                Worker
                   │
                   ▼
         Permission Manager
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
 Workspace     Command      Network
 Sandbox       Validator    Policy
      │
      ▼
 Tool Execution Engine
```

Every external action passes through all applicable layers.

---

# 13.4 Trust Boundaries

AI Loom defines three trust zones.

```text
Workspace
──────────────
Trusted

User Approved Resources
──────────────
Conditionally Trusted

Everything Else
──────────────
Untrusted
```

Workers may never cross trust boundaries without permission.

---

# 13.5 Permission Levels

Every operation belongs to one level.

```text
SAFE

MODERATE

ELEVATED

DANGEROUS
```

---

## SAFE

Examples:

```text
Read file

Search symbols

Git status

List directory

Read configuration
```

Always allowed.

---

## MODERATE

Examples:

```text
Write file

Patch file

Create file

Rename file
```

Usually allowed inside the workspace.

---

## ELEVATED

Examples:

```text
Delete file

Install packages

Git commit

Modify build configuration
```

Usually require confirmation.

---

## DANGEROUS

Examples:

```text
Recursive delete

Network access

Execute downloaded scripts

Modify files outside workspace

Shell with unrestricted permissions
```

Require explicit approval every time.

---

# 13.6 Permission Policy

Policy object:

```text
PermissionPolicy

filesystem

terminal

network

git

packages

browser

external_tools
```

Each field:

```text
ALLOW

ASK

DENY
```

Example:

```yaml
filesystem: ALLOW
terminal: ASK
network: DENY
packages: ASK
git: ASK
```

---

# 13.7 Workspace Isolation

Every execution is confined to one workspace.

Example:

```text
/home/sid/project/
```

Allowed:

```text
/home/sid/project/src
```

Denied:

```text
/etc/

/usr

/home/sid/.ssh

/home/sid/Documents
```

unless explicitly authorised.

---

# 13.8 Canonical Path Validation

Every filesystem operation follows:

```text
Input

↓

Normalise

↓

Resolve Symlinks

↓

Canonical Path

↓

Inside Workspace?

↓

Execute
```

Relative paths alone are never trusted.

---

# 13.9 Symlink Protection

Example:

```text
workspace/

↓

evil_link

↓

/etc/passwd
```

Canonical resolution detects the escape.

Operation is rejected.

---

# 13.10 Command Validation

Every command is classified.

Examples:

Safe:

```text
pytest

npm test

cargo test

black

ruff

git status
```

Moderate:

```text
npm install

pip install
```

Dangerous:

```text
curl | bash

sudo rm -rf /

chmod -R 777 /

wget unknown.sh
```

Classification occurs before execution.

---

# 13.11 Shell Restrictions

Default shell environment:

* Non-interactive
* Explicit working directory
* Controlled environment variables
* No implicit shell startup scripts
* Configurable PATH

Interactive shells are not permitted.

---

# 13.12 Package Installation

Package installation is considered high risk.

Flow:

```text
Worker

↓

Planner Recommendation

↓

Permission Check

↓

User Approval

↓

Installation

↓

Index Refresh
```

Workers cannot silently install dependencies.

---

# 13.13 Network Policy

Network access is disabled by default.

Allowed only if policy permits.

Examples:

Allowed:

* Fetch official documentation
* Download approved dependency
* Access configured MCP server

Denied:

* Arbitrary websites
* Unknown APIs
* Background telemetry

---

# 13.14 Git Safety

Read-only Git operations:

```text
Status

Diff

Log

Branch
```

Always safe.

Mutating operations:

```text
Commit

Push

Reset

Rebase

Cherry-pick
```

Require permission.

---

# 13.15 File Deletion

Deletion flow:

```text
Delete Request

↓

Permission

↓

Optional Approval

↓

Move to Recovery Area

↓

Permanent Removal (optional)
```

Recovery area expiration is configurable.

---

# 13.16 Atomic Writes

Every write follows:

```text
Write Temp File

↓

Verify

↓

Atomic Rename

↓

Update Index
```

This prevents partially written files.

---

# 13.17 Approval Workflow

Approval request contains:

```text
Operation

Reason

Affected Files

Risk

Reversible?

Estimated Impact
```

Example:

```text
Install package:

fastapi

Reason:

Required for requested feature.

Risk:

Medium

Reversible:

Yes
```

---

# 13.18 Dry Run Mode

Every mutating operation may support:

```text
dry_run = true
```

Returns:

```text
Files affected

Commands

Expected Changes

Validation Results
```

Nothing is modified.

---

# 13.19 Rate Limiting

Prevent runaway execution.

Limits include:

* Maximum tool calls per minute
* Maximum shell commands
* Maximum file writes
* Maximum retries

Exceeding limits pauses execution.

---

# 13.20 Resource Limits

Configurable limits:

```text
CPU

Memory

Disk

Execution Time

Output Size

File Size
```

Workers cannot consume unlimited resources.

---

# 13.21 Timeout Policy

Every tool defines:

```text
Soft Timeout

Hard Timeout
```

Example:

```text
Tests

Soft:
30 seconds

Hard:
5 minutes
```

Hard timeout terminates execution.

---

# 13.22 Secret Protection

Workers never receive:

* API keys
* SSH keys
* Passwords
* Tokens

unless explicitly injected.

Secret scanning detects accidental exposure.

Example patterns:

```text
AWS Keys

GitHub Tokens

JWT Secrets

Private Keys
```

---

# 13.23 Audit Trail

Every privileged action records:

```text
Timestamp

Worker

Task

Tool

Arguments

Permission Decision

Result

Duration
```

Audit logs are append-only.

---

# 13.24 Recovery

Every mutating action stores:

```text
Before Hash

After Hash

Timestamp

Worker

Task
```

Enables:

* rollback
* debugging
* replay

---

# 13.25 Policy Profiles

Example profiles:

Development:

```yaml
filesystem: ALLOW
terminal: ALLOW
packages: ASK
network: ASK
git: ASK
```

Review:

```yaml
filesystem: READ_ONLY
terminal: DENY
packages: DENY
network: DENY
git: READ_ONLY
```

CI Mode:

```yaml
filesystem: LIMITED
terminal: ALLOW
packages: DENY
network: LIMITED
git: READ_ONLY
```

---

# 13.26 Human Override

The user may explicitly approve an operation.

Overrides apply only to:

* current task
* current session
* permanently (optional)

Never assume future approval.

---

# 13.27 Safe Defaults

Default behaviour:

* Allow reads
* Allow indexing
* Allow patches inside workspace
* Ask before installing
* Ask before deleting
* Ask before network
* Deny workspace escape

Safe by default.

---

# 13.28 Observability

Security events:

```text
PermissionRequested

PermissionGranted

PermissionDenied

WorkspaceEscapeBlocked

SecretDetected

CommandRejected

ApprovalRequested
```

Useful for monitoring and debugging.

---

# 13.29 Security Testing

Every tool must include tests for:

* Path traversal
* Symlink escape
* Permission enforcement
* Invalid arguments
* Cancellation
* Timeout
* Rollback metadata

Security tests are mandatory.

---

# 13.30 Design Constraints

1. Workers never access the operating system directly.
2. Every external action passes through the Permission Manager.
3. Workspace isolation cannot be bypassed.
4. All paths are canonicalised before execution.
5. Network access is opt-in.
6. Secrets are never exposed by default.
7. Every privileged action is logged.
8. Every write is atomic.
9. Unsafe defaults are prohibited.
10. Permission decisions are deterministic.

---

# Architect's Notes (Normative)

## 1. Consider Running Workers in a Sandbox

For Version 2, execute tool actions inside an isolated runtime.

Possible implementations:

```text
Firejail

Bubblewrap (bwrap)

Rootless Docker

Podman

Lightweight VM
```

The orchestration layer should not depend on a specific sandbox implementation.

---

## 2. Separate Tool Permissions from Model Trust

Never assume a stronger model is more trustworthy.

Permission decisions must depend only on:

* operation
* policy
* user approval

Never on the selected LLM.

---

## 3. Introduce Capability Tokens

Instead of giving workers unrestricted tool access, issue short-lived capability tokens.

Example:

```text
Task

↓

Granted:
Read auth.py

Write auth.py

Run pytest

↓

Cannot access any other tool
```

This follows the principle of least privilege and reduces the impact of erroneous tool requests.

---

## 4. Add Approval Policies

Support configurable approval strategies.

Examples:

```text
Always Ask

Ask Once Per Session

Ask Once Per Workspace

Never Ask (Trusted Workspace)

Always Deny
```

This allows users to balance convenience with security while preserving the same architecture.

---

## 5. Treat the Workspace as Immutable Until Commit

Internally, think of every modification as a transaction.

```text
Read

↓

Patch

↓

Validate

↓

Commit

↓

Update Index
```

If validation fails, the transaction can be rolled back without leaving the repository in a partially modified state.

This transactional mindset will make future features such as undo, collaborative editing and distributed execution much easier to implement.

---
