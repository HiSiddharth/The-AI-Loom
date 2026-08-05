# AI Loom - ⚠️ This project is a work in progress

> **A local-first, multi-model, agentic software engineering platform.**

AI Loom is an intelligent coding system designed to orchestrate planning, implementation, validation, repository understanding and memory using both local and remote Large Language Models (LLMs).

Unlike traditional AI coding assistants, AI Loom separates **planning**, **implementation**, **context retrieval**, **validation**, and **tool execution** into independent components that cooperate through a well-defined architecture.

The project is designed to be:

* 🖥️ Local-first
* 🧠 Multi-model
* 🔌 Provider agnostic
* 📚 Repository aware
* 🛡️ Secure by default
* ✅ Validation driven
* ⚡ Extensible
* 📦 Offline capable

---

# Architecture Documentation

The complete architecture specification is available in the `ArchitectureDoc/` directory.

## Core Architecture

| Chapter    | Document                                                        |
| ---------- | --------------------------------------------------------------- |
| Chapter 1  | [Introduction & Design Philosophy](ArchitectureDoc/Chapter1.md) |
| Chapter 2  | [System Overview](ArchitectureDoc/Chapter2.md)                  |
| Chapter 3  | [Planner Architecture](ArchitectureDoc/Chapter3.md)             |
| Chapter 4  | [Worker Architecture](ArchitectureDoc/Chapter4.md)              |
| Chapter 5  | [Model Routing System](ArchitectureDoc/Chapter5.md)             |
| Chapter 6  | [Context Engine](ArchitectureDoc/Chapter6.md)                   |
| Chapter 7  | [Repository Indexing](ArchitectureDoc/Chapter7.md)              |
| Chapter 8  | [Memory System](ArchitectureDoc/Chapter8.md)                    |
| Chapter 9  | [Tool Execution Engine](ArchitectureDoc/Chapter9.md)            |
| Chapter 10 | [Permission & Security Model](ArchitectureDoc/Chapter10.md)     |

---

## Infrastructure

| Chapter    | Document                                                             |
| ---------- | -------------------------------------------------------------------- |
| Chapter 11 | [Event Bus & Observability](ArchitectureDoc/Chapter11.md)            |
| Chapter 12 | [Provider Abstraction Layer](ArchitectureDoc/Chapter12.md)           |
| Chapter 13 | [Data Storage & Persistence](ArchitectureDoc/Chapter13.md)           |
| Chapter 14 | [Context Lifecycle & Token Management](ArchitectureDoc/Chapter14.md) |
| Chapter 15 | [Plugin System & Extensibility](ArchitectureDoc/Chapter15.md)        |
| Chapter 16 | [Deployment, Configuration & Runtime](ArchitectureDoc/Chapter16.md)  |

---

## Reliability & Specifications

| Chapter    | Document                                                                  |
| ---------- | ------------------------------------------------------------------------- |
| Chapter 17 | [Testing, Validation & Quality Assurance](ArchitectureDoc/Chapter17.md)   |
| Chapter 18 | [AI Loom Protocol (ALP)](ArchitectureDoc/Chapter18.md)                    |
| Chapter 19 | [Development Roadmap & Implementation Plan](ArchitectureDoc/Chapter19.md) |
| Chapter 20 | [AI Loom v1.0 Technical Specification](ArchitectureDoc/Chapter20.md)      |

---

## Appendices

| Appendix   | Document                                                                         |
| ---------- | -------------------------------------------------------------------------------- |
| Appendix A | [Engineering Decisions & Recommended Technologies](ArchitectureDoc/AppendixA.md) |
| Appendix B | [Repository Layout & File-by-File Specification](ArchitectureDoc/AppendixB.md)   |
| Appendix C | [AI Loom MVP (v0.1) Implementation Blueprint](ArchitectureDoc/AppendixC.md)      |

---

# Recommended Reading Order

For readers new to AI Loom:

1. [Chapter 1 – Introduction & Design Philosophy](ArchitectureDoc/Chapter1.md)
2. [Chapter 2 – System Overview](ArchitectureDoc/Chapter2.md)
3. [Chapter 3 – Planner Architecture](ArchitectureDoc/Chapter3.md)
4. [Chapter 4 – Worker Architecture](ArchitectureDoc/Chapter4.md)
5. [Chapter 6 – Context Engine](ArchitectureDoc/Chapter6.md)
6. [Chapter 7 – Repository Indexing](ArchitectureDoc/Chapter7.md)
7. [Chapter 9 – Tool Execution Engine](ArchitectureDoc/Chapter9.md)
8. [Chapter 17 – Testing, Validation & Quality Assurance](ArchitectureDoc/Chapter17.md)
9. [Chapter 20 – AI Loom v1.0 Technical Specification](ArchitectureDoc/Chapter20.md)
10. [Appendix C – AI Loom MVP (v0.1) Implementation Blueprint](ArchitectureDoc/AppendixC.md)

---

# High-Level Architecture

```text
                     User
                       │
                       ▼
               OpenCode / CLI
                       │
                       ▼
                AI Loom Runtime
                       │
      ┌────────────────┼────────────────┐
      ▼                ▼                ▼
  Planner        Context Engine     Tool Engine
      │                │
      ▼                ▼
 Model Router   Repository Index
      │                │
      ▼                ▼
   Worker       Project Memory
      │
      ▼
  Validation
      │
      ▼
    Response
```

---

# Reference MVP Stack

| Component        | Technology             |
| ---------------- | ---------------------- |
| Planner Model    | Qwen 3.6 27B           |
| Worker Model     | Qwen 3.5 9B            |
| Provider         | LM Studio              |
| Repository Index | Tree-sitter            |
| Storage          | SQLite                 |
| Runtime          | Python + asyncio       |
| Validation       | Native project tooling |
| User Interface   | OpenCode               |

---

# Project Status

* ✅ Complete Architecture Specification
* ✅ Technical Specification
* ✅ Repository Layout
* ✅ MVP Blueprint
* 🚧 Implementation in Progress

---

# Repository Structure

```text
.
├── ArchitectureDoc/
│   ├── Chapter1.md
│   ├── ...
│   ├── Chapter20.md
│   ├── AppendixA.md
│   ├── AppendixB.md
│   ├── AppendixC.md
│   └── index.md
├── README.md
└── (implementation)
```

---

# Vision

AI Loom is not intended to be another AI chatbot with coding tools.

Its goal is to become a **software engineering platform** that combines specialised planning, repository understanding, implementation, validation, memory and orchestration into a cohesive, extensible system capable of tackling real-world software engineering tasks.
