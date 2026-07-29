# AI Loom Architecture Specification

# Chapter 11 — Model Router & Multi-Model Orchestration

**Version:** 1.0 Draft

---

# 11.1 Purpose

The Model Router is responsible for selecting the most appropriate model for every reasoning task.

The rest of AI Loom never knows which model is being used.

Instead, every subsystem requests **capabilities**, not models.

This allows:

* Switching models without changing code
* Running local and cloud models interchangeably
* Falling back when models fail
* Optimising for speed, cost and quality

---

# 11.2 Philosophy

The router answers one question:

> **"Given this task, which model is most suitable?"**

Not:

> "Which model is available?"

Capability drives selection.

---

# 11.3 Responsibilities

The router is responsible for:

* Model selection
* Model fallback
* Context budgeting
* Load balancing
* Health monitoring
* Capability matching
* Token accounting
* Provider abstraction

It is **not** responsible for:

* Planning
* Prompt construction
* Tool execution
* Context retrieval

---

# 11.4 High-Level Architecture

```text
Planner

Worker

Reviewer

↓

Model Router

↓

Capability Resolver

↓

Provider Manager

↓

LM Studio
Ollama
OpenAI
Anthropic
Gemini
OpenRouter

↓

Model
```

---

# 11.5 Why a Router?

Without a router:

```text
Planner

↓

Qwen 27B
```

Hardcoded.

Changing models requires changing code.

With a router:

```text
Planner

↓

Needs:

High Reasoning

↓

Router

↓

Qwen 27B
```

Tomorrow:

```text
↓

DeepSeek

↓

No code changes.
```

---

# 11.6 Capability Model

Instead of model names:

```text
High Reasoning

Large Context

Low Latency

Vision

Coding

JSON

Tool Calling
```

Capabilities are abstract.

---

# 11.7 Capability Schema

Every model advertises:

```text
ModelCapability

Reasoning

Coding

Context

Latency

Cost

Tool Support

JSON Reliability

Streaming

Vision

Availability
```

---

# 11.8 Capability Levels

Reasoning:

```text
LOW

MEDIUM

HIGH

EXPERT
```

Coding:

```text
BASIC

GOOD

ADVANCED

SPECIALIST
```

Latency:

```text
FAST

NORMAL

SLOW
```

Context:

Numeric:

```text
8k

16k

32k

64k

128k

256k
```

---

# 11.9 Model Registry

Example:

```text
Qwen 3.5 9B

Reasoning:
MEDIUM

Coding:
ADVANCED

Latency:
FAST

Context:
64k
```

```text
Qwen 3.6 27B

Reasoning:
EXPERT

Coding:
SPECIALIST

Latency:
SLOW

Context:
16k
```

Router uses capabilities instead of names.

---

# 11.10 Request Flow

```text
Worker

↓

Requires

Advanced Coding

↓

Router

↓

Best Model

↓

Provider

↓

Inference
```

---

# 11.11 Request Object

Subsystems send:

```text
InferenceRequest

Capability Requirements

Temperature

Max Tokens

Context Budget

Streaming

JSON Required
```

No model name.

---

# 11.12 Response Object

Router returns:

```text
InferenceResponse

Model Used

Provider

Latency

Usage

Output

Diagnostics
```

---

# 11.13 Planner Routing

Planner requests:

```text
Reasoning

EXPERT

Coding

GOOD

Latency

LOW PRIORITY
```

Likely result:

Large reasoning model.

---

# 11.14 Worker Routing

Worker requests:

```text
Coding

SPECIALIST

Latency

FAST

Reasoning

MEDIUM
```

Likely result:

Smaller coding model.

---

# 11.15 Review Routing

Reviewer requests:

```text
Reasoning

HIGH

Coding

HIGH

JSON

STRICT
```

Often different from Worker.

---

# 11.16 Context-Aware Routing

Example:

Context:

```text
120k tokens
```

Planner requests:

```text
32k
```

Router rejects.

Instead:

```text
Large Context Model
```

Capability constraints override preference.

---

# 11.17 Provider Abstraction

Every provider implements:

```python
class Provider:

    chat()

    stream()

    list_models()

    health()

    embeddings()

    supports_tools()
```

Examples:

* LM Studio
* Ollama
* OpenAI-compatible APIs
* Anthropic
* Gemini

Workers never know which provider is used.

---

# 11.18 Provider Health

Router continuously tracks:

```text
Available

Offline

Busy

Rate Limited

Loading
```

Unhealthy providers are skipped.

---

# 11.19 Local Model Loading

Some providers load models lazily.

Example:

```text
Planner

↓

Need 27B

↓

LM Studio

↓

Load Model

↓

Execute

↓

Unload Later
```

The router hides this latency from callers.

---

# 11.20 Model Warm Pool (Future)

Frequently used models remain loaded.

Example:

```text
9B

Loaded

27B

Loaded

70B

Unloaded
```

Reduces switching latency.

---

# 11.21 Fallback Strategy

If inference fails:

```text
Primary

↓

Retry

↓

Alternative Provider

↓

Alternative Model

↓

Planner Notification
```

Retries preserve the original request.

---

# 11.22 Token Budgeting

Before inference:

```text
Prompt

↓

Estimate Tokens

↓

Fits?

↓

Yes

↓

Execute
```

Otherwise:

```text
↓

Request Smaller Context

or

Trigger Compression
```

Router never silently truncates prompts.

---

# 11.23 Cost Awareness

Every model has metadata.

```text
Latency

Memory

Energy

Network

Licence

Estimated Cost
```

Selection policies may optimise for:

* speed
* quality
* local-only
* lowest cost

---

# 11.24 Model Affinity

Tasks may express preferences.

Example:

```text
Coding

↓

Prefer Coding Specialists
```

But preferences are not mandatory.

The router makes the final decision.

---

# 11.25 Session Affinity

Within one session:

```text
Planner

↓

Same Planner Model
```

Avoid unnecessary switching.

Worker tasks may still use different models.

---

# 11.26 Streaming

Supported providers expose:

```text
Token

↓

Token

↓

Token
```

The router normalises streaming APIs.

Callers receive a unified interface.

---

# 11.27 Structured Output

If JSON required:

Router enables:

* JSON mode
* constrained decoding
* schema validation (where supported)

If unavailable:

Post-validation is performed before returning results.

---

# 11.28 Performance Metrics

Collected per request:

* Model selected
* Provider
* Queue time
* Load time
* Prompt tokens
* Completion tokens
* Inference latency
* Throughput (tokens/sec)
* Success/failure

---

# 11.29 Configuration

Example:

```yaml
routing:

  planner:
    reasoning: expert

  worker:
    coding: specialist
    latency: fast

  reviewer:
    reasoning: high
```

Model names remain outside business logic.

---

# 11.30 Design Constraints

1. No subsystem hardcodes model names.
2. Routing decisions are deterministic given the same registry and policy.
3. Router validates context limits before inference.
4. Router hides provider-specific APIs.
5. Router supports graceful fallback.
6. Providers are hot-swappable.
7. Capability matching takes precedence over preferences.
8. Every inference is logged.

---

# Architect's Notes (Normative)

## 1. Separate Routing Policy from Capability Registry

Maintain two independent components.

**Capability Registry**

```text
Qwen 3.5 9B

↓

Capabilities
```

**Routing Policy**

```text
Planner

↓

Needs Expert Reasoning

↓

Choose Best Available
```

Changing policy should never require editing model definitions.

---

## 2. Use Model Profiles

Instead of repeatedly specifying capabilities, define reusable profiles.

Example:

```yaml
profiles:

  planner:
    reasoning: expert
    coding: advanced

  worker:
    coding: specialist
    latency: fast

  reviewer:
    reasoning: high
    json: strict
```

Subsystems request profiles rather than individual capability fields.

---

## 3. Support Multi-Step Escalation

One of AI Loom's biggest advantages should be progressive escalation.

Example:

```text
Task

↓

9B Worker

↓

Success?

↓

Yes → Done

↓

No

↓

27B Worker

↓

Success?

↓

Yes → Done

↓

No

↓

Planner Intervention
```

Most tasks should never reach the largest model.

---

## 4. Add Adaptive Routing

The router should learn from execution history.

Example:

```text
Task Type

↓

Past Success Rate

↓

Model Ranking

↓

Selection
```

If the 9B model consistently succeeds on React components but struggles with C++ templates, the router should gradually adapt its preferences.

This learning should be optional and transparent.

---

## 5. Your Initial Hardware Strategy

For your RTX 4060 (8 GB VRAM) + 24 GB RAM setup, the default routing policy should be:

```text
Planner
──────────────
Primary:
Qwen 3.6 27B

Worker
──────────────
Primary:
Qwen 3.5 9B

Reviewer
──────────────
Primary:
Qwen 3.6 27B

Indexer
──────────────
No LLM unless summaries are needed

Context Engine
──────────────
No LLM

Tool Engine
──────────────
No LLM
```

This matches your original objective:

* Use the larger model only for high-level reasoning and reviews.
* Let the 9B model handle the majority of coding work in fresh, task-specific contexts.
* Keep the expensive 27B model out of the tight execution loop whenever possible.

As your hardware or available models improve, only the routing policy needs to change—the rest of the architecture remains unchanged.

---

