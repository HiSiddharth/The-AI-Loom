# AI Loom Architecture Specification

# Chapter 18 — AI Loom Protocol (ALP): Internal Communication Specification

**Version:** 1.0 Draft

---

# 18.1 Purpose

Every major component in AI Loom communicates using a common protocol.

The protocol defines **what** components say to each other, not **how** they communicate.

Whether components run:

* inside one process,
* across multiple processes,
* on different machines,

the protocol remains identical.

This future-proofs the architecture for distributed execution.

---

# 18.2 Design Philosophy

ALP should be:

* Strongly typed
* Versioned
* Self-describing
* Extensible
* Deterministic
* Transport-agnostic

Components exchange structured messages rather than arbitrary Python objects.

---

# 18.3 Architecture

```text
Planner

↓

Task Queue

↓

Worker

↓

Tool Engine

↓

Validation

↓

Planner

↓

Completed
```

Every arrow represents ALP messages.

---

# 18.4 Message Categories

ALP defines six categories.

```text
Commands

Events

Requests

Responses

Notifications

Heartbeats
```

Each has different semantics.

---

# 18.5 Commands

Commands instruct another component to perform an action.

Examples:

```text
ExecuteTask

RunTool

RetrieveContext

IndexWorkspace

ValidateTask
```

Commands expect completion.

---

# 18.6 Events

Events describe something that has already happened.

Examples:

```text
TaskCreated

TaskCompleted

FileIndexed

WorkerStarted

ModelLoaded

PermissionGranted
```

Events are immutable.

---

# 18.7 Requests

Requests ask for information.

Examples:

```text
GetContext

GetMemory

ListProviders

GetConfiguration

GetHealth
```

Requests expect responses.

---

# 18.8 Responses

Responses contain results.

Example:

```text
ContextResponse

ValidationResponse

InferenceResponse

MemoryResponse
```

Responses reference the originating request.

---

# 18.9 Notifications

Notifications communicate information that does not require acknowledgement.

Examples:

```text
ProgressUpdate

Typing

StreamingToken

IndexProgress
```

---

# 18.10 Heartbeats

Used only by long-running services.

```text
Planner Alive

Worker Alive

Provider Alive
```

Useful for distributed deployments.

---

# 18.11 Common Message Schema

Every ALP message contains:

```text
id

timestamp

protocol_version

session_id

workspace_id

sender

recipient

message_type

payload

metadata
```

No component-specific fields exist at the top level.

---

# 18.12 Message IDs

Every message receives a globally unique ID.

Example:

```text
msg_01HXZ...

msg_01HXA...

msg_01HXB...
```

IDs enable tracing and replay.

---

# 18.13 Correlation IDs

A request may generate multiple downstream messages.

```text
Planner Request

↓

Worker

↓

Tool

↓

Validation
```

All share the same correlation ID.

This enables complete execution tracing.

---

# 18.14 Payload Schema

Payloads are versioned separately.

Example:

```json
{
  "task_id": "...",
  "priority": "high",
  "objective": "...",
  "constraints": [...]
}
```

Components validate payloads before processing.

---

# 18.15 Message Validation

Every message passes through validation.

Checks include:

* Required fields
* Version compatibility
* Payload schema
* Size limits
* Permissions

Invalid messages are rejected.

---

# 18.16 Task Messages

Example:

```text
ExecuteTask

↓

task_id

objective

constraints

context

validation_profile
```

Workers never receive raw planner state.

---

# 18.17 Tool Messages

Example:

```text
RunTool

↓

tool_name

arguments

permissions

timeout
```

The Tool Engine validates before execution.

---

# 18.18 Context Messages

Example:

```text
RetrieveContext

↓

symbols

files

budget

strategy
```

The Context Engine decides retrieval details.

---

# 18.19 Validation Messages

Example:

```text
ValidateTask

↓

task_id

changed_files

validators

policy
```

Validation remains independent from Workers.

---

# 18.20 Model Messages

Example:

```text
InferenceRequest

↓

profile

context

prompt

constraints
```

Notice:

No model name appears.

Routing happens later.

---

# 18.21 Error Messages

Errors use a standard schema.

```text
error_code

component

severity

recoverable

details

diagnostics
```

Example:

```text
MODEL_UNAVAILABLE

Recoverable:
Yes
```

---

# 18.22 Streaming Messages

Streaming responses consist of multiple messages.

```text
Start

↓

Chunk

↓

Chunk

↓

Chunk

↓

Complete
```

Consumers reconstruct the final output.

---

# 18.23 Cancellation

Long-running tasks support cancellation.

Flow:

```text
CancelTask

↓

Worker

↓

Cleanup

↓

Cancelled
```

Cancellation should be cooperative whenever possible.

---

# 18.24 Retry Semantics

Commands define retry behaviour.

Examples:

```text
Inference

Retry

Filesystem

No Retry

Delete

No Retry

Network

Retry
```

Retries must be idempotent where applicable.

---

# 18.25 Timeouts

Every request defines:

```text
Soft Timeout

Hard Timeout
```

Timeouts propagate through dependent requests.

---

# 18.26 Versioning

ALP uses semantic versioning.

Example:

```text
Protocol

1.0

Payload

1.2
```

Breaking changes increment the major version.

---

# 18.27 Compatibility

Older components may continue operating if:

* Message version is compatible
* Payload fields are optional
* Unknown fields are ignored

Strict compatibility rules improve gradual upgrades.

---

# 18.28 Security

Messages include:

```text
Permissions

Workspace

Session

Capabilities
```

Recipients validate permissions before execution.

---

# 18.29 Serialization

Recommended formats:

Version 1:

```text
JSON
```

Future:

```text
MessagePack

Protocol Buffers

FlatBuffers
```

Transport remains independent.

---

# 18.30 Transport Independence

ALP should work over:

```text
In-memory Queue

Async Channels

TCP

WebSocket

gRPC

Unix Socket

HTTP
```

Changing transport should not require protocol changes.

---

# 18.31 Recording

Every message may optionally be recorded.

Benefits:

* Replay
* Debugging
* Performance analysis
* Regression testing

Recorded sessions should be deterministic where possible.

---

# 18.32 Design Constraints

1. Every message is versioned.
2. Messages are immutable.
3. Components communicate only through ALP.
4. Payloads are schema-validated.
5. Messages are transport-independent.
6. Correlation IDs enable tracing.
7. Unknown optional fields are ignored.
8. Messages never contain chain-of-thought.
9. Security metadata accompanies privileged requests.
10. Protocol changes are backwards-compatible whenever possible.

---

# Architect's Notes (Normative)

## 1. Think Like a Distributed System From Day One

Even if AI Loom initially runs in a single Python process, every component should communicate through ALP.

Later, replacing:

```text
Local Worker
```

with:

```text
Remote Worker
```

should require changing only the transport layer.

---

## 2. Use Strongly Typed Models

Represent every ALP message as a validated Python model (for example, with Pydantic).

Benefits:

* Validation
* Better IDE support
* Easier testing
* Clear documentation
* Automatic schema generation

Avoid passing raw dictionaries between components.

---

## 3. Keep Business Logic Out of the Transport

The transport layer should only deliver messages.

It must never decide:

* which Worker to use
* which model to select
* whether permissions are granted

Those decisions belong to higher-level services.

---

## 4. Make ALP Observable

Every message should automatically emit lifecycle events:

```text
Message Sent

↓

Message Received

↓

Message Processed

↓

Message Completed
```

This integrates naturally with the Observability System and enables full end-to-end tracing.

---

## 5. Build AI Loom Like a Microkernel

The most important architectural principle of ALP is this:

The protocol is the stable foundation.

Everything else—Planner, Workers, Providers, Tools, Validation, Memory and future distributed services—should be replaceable as long as they continue speaking ALP.

This approach will let AI Loom grow from a local coding assistant into a scalable, distributed AI engineering platform without requiring a redesign of its internal communication model.

---