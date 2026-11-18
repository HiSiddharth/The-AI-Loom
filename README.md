
# The AI Loom 

> **A local-first, multi-model coding orchestrator with dynamic VRAM management and execution-driven self-correction.**

AI Loom is a LangGraph-based agentic workflow designed to run multi-model software engineering loops locally via **LM Studio**. Instead of relying on a single large model, it separates **Planning**, **Implementation**, and **Verification** across specialized local models—dynamically swapping them in and out of GPU VRAM to fit consumer hardware constraints.

---

## Architecture (Current Working Pipeline)

```text
                       ┌──────────────────────┐
                       │    User Objective    │
                       │    (CLI / Config)    │
                       └──────────┬───────────┘
                                  ▼
                       ┌──────────────────────┐
                       │     Planner Node     │◄─────────────────────┐
                       │   (Qwen 3.5 9B)      │                      │
                       └──────────┬───────────┘                      │
                                  │ [Unload 9B -> Load 4B]           │
                                  ▼                                  │
                     (Valid task plan generated?)                    │
                        │                   │                        │
                       Yes                 No                        │
                        │                   ▼                        │
                        │                  END                       │
                        ▼                                            │
         ┌─────────────────────────────┐                             │
         │         Worker Node         │                             │
         │   (Qwen 3 4B Thinking)      │                             │
         │  ┌───────────────────────┐  │                             │
         │  │ Generate -> Subprocess│  │                             │
         │  │   Run -> Feed stderr  │  │                             │
         │  │   back on failure     │  │                             │
         │  └───────────────────────┘  │                             │
         └──────────────┬──────────────┘                             │
                        │ [All tasks done: Unload 4B -> Load 9B]     │
                        ▼                                            │
         ┌─────────────────────────────┐                             │
         │        Verifier Node        │                             │
         │       (Qwen 3.5 9B)         │                             │
         │ Reviews code + run outputs  │                             │
         └──────────────┬──────────────┘                             │
                        │                                            │
              ┌─────────┴─────────┐                                  │
        STATUS: APPROVED    STATUS: REVISE                           │
              │                   └──────────────────────────────────┘
              ▼                     (Up to MAX_MANAGER_RETRIES)
             END
```

---

## Key Features Implemented

* **Dynamic VRAM Lifecycle Management (`hardware.py`):** Explicitly unloads the active model via LM Studio's REST API (`/api/v0/models`, `/api/v1/models/load`, `/api/v1/models/unload`) before loading the next stage's model, allowing multi-model orchestration on single-GPU setups.
* **Stateful LangGraph Orchestration (`graph.py`, `nodes.py`):** Coordinates task decomposition, sequential code generation, bounded retries, and manager feedback loops.
* **Execution-Grounded Self-Correction:** The Worker executes each generated script via `subprocess` inside `./sandbox` and feeds captured `stderr` / tracebacks and prior code back into subsequent attempts.
* **Thinking-Model Output Sanitization:** Strips `<think>...</think>` reasoning traces before parsing JSON task plans, Python code blocks, or verification verdicts.
* **Observability:** Streams node transitions, execution outputs, VRAM swap timings, and review verdicts to both stdout and `./sandbox/platform.log`.

---

## Project Structure

```text
.
├── main.py              # CLI entrypoint, logging setup, and pipeline runner
├── config.py            # Model IDs, retry limits, workspace path, and system prompts
├── graph.py             # LangGraph StateGraph wiring and conditional edges
├── nodes.py             # Planner, Worker, and Verifier nodes + routing logic
├── hardware.py          # LM Studio API client for dynamic VRAM loading/unloading
├── opencode.json        # OpenCode LM Studio provider configuration
└── ArchitectureDoc/     # Long-term v1.0 design specifications & roadmap docs
```

---

## Quick Start

### Prerequisites
* Python 3.10+
* [LM Studio](https://lmstudio.ai/) running locally on `http://localhost:1234` with the server enabled
* Models downloaded in LM Studio (configured in `config.py`):
  * Planner / Verifier: `qwen/qwen3.5-9b`
  * Worker: `qwen/qwen3-4b-thinking-2507`

### Installation & Run
```bash
pip install langgraph langchain-openai langchain-core requests

# Run with a custom objective via CLI
python main.py --objective "Create calculator.py with add/divide functions and test_calculator.py using pytest, ensuring division by zero raises ValueError."

# Or run using the default objective in config.py
python main.py
```

Generated scripts and `platform.log` are written to `./sandbox/`.

---

## Current Limitations & Security Notice

* **Directory-Scoped Execution (Not OS Isolation):** Generated scripts are currently executed with `cwd="./sandbox"` via Python's `subprocess`, which is **not** a hardened OS or container sandbox. Do not run untrusted objectives on sensitive host machines until container isolation is implemented.
* **Single-File Step Execution:** Currently validates scripts individually via `python <filename>`. Automated `pytest` suite detection is planned next.

---

## Roadmap (Towards v1.0)

The full long-term architectural vision is documented in [`ArchitectureDoc/`](ArchitectureDoc/Chapter1.md). Planned milestones include:
- [ ] Ephemeral Docker container execution (`--network none`) for true sandboxing
- [ ] `pytest` / linter integration inside the Worker validation step
- [ ] Tree-sitter repository indexing & SQLite project memory
- [ ] Async provider abstraction & OpenCode CLI integration