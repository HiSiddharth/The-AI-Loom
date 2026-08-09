import os
import requests
import json
import logging
from typing import TypedDict, List, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from config import (
    WORKSPACE,
    LOG_FILE,
    LM_STUDIO_HOST,
    BASE_URL,
    PLANNER_MODEL_ID,
    WORKER_MODEL_ID,
    PLANNER_SYSTEM_PROMPT,
    WORKER_SYSTEM_PROMPT,
    VERIFIER_SYSTEM_PROMPT,
    OBJECTIVE
)

# ---------------------------------------------------------
# SETUP DUAL LOGGING (Console + Timewise Log File)
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MiniPlatform")

# ---------------------------------------------------------
# LANGGRAPH STATE DEFINITION
# ---------------------------------------------------------
class PlatformState(TypedDict):
    objective: str
    tasks: List[Dict[str, Any]]
    current_task_index: int
    generated_files: Dict[str, str]
    verification_report: str

# ---------------------------------------------------------
# LM STUDIO HARDWARE MANAGEMENT HELPERS
# ---------------------------------------------------------
def unload_all_models():
    logger.info("[VRAM MANAGER] Clearing all models from memory...")
    try:
        res = requests.get(f"{LM_STUDIO_HOST}/api/v0/models")
        if res.status_code == 200:
            for m in res.json().get("data", []):
                if instance_id := m.get("id"):
                    logger.info(f"-> Unloading instance: {instance_id}")
                    requests.post(f"{LM_STUDIO_HOST}/api/v1/models/unload", json={"instance_id": instance_id})
        logger.info("[SUCCESS] VRAM completely cleared.")
    except Exception as e:
        logger.warning(f"Unload skipped/failed: {e}")

def unload_model_by_identifier(model_identifier):
    logger.info(f"[VRAM MANAGER] Unloading model: {model_identifier}...")
    try:
        res = requests.get(f"{LM_STUDIO_HOST}/api/v0/models")
        if res.status_code == 200:
            for m in res.json().get("data", []):
                if model_identifier in m.get("id", "") or model_identifier in m.get("identifier", ""):
                    requests.post(f"{LM_STUDIO_HOST}/api/v1/models/unload", json={"instance_id": m.get("id")})
                    logger.info(f"[SUCCESS] Unloaded {model_identifier}")
                    return
        requests.post(f"{LM_STUDIO_HOST}/api/v1/models/unload", json={"model": model_identifier})
    except Exception as e:
        logger.warning(f"Selective unload error: {e}")

def load_model(model_identifier):
    logger.info(f"[VRAM MANAGER] Loading model into VRAM: {model_identifier}...")
    try:
        res = requests.post(f"{LM_STUDIO_HOST}/api/v1/models/load", json={"model": model_identifier, "flash_attention": True})
        if res.status_code == 200:
            logger.info(f"[SUCCESS] Loaded {model_identifier}")
        else:
            logger.error(f"[ERROR] Load failed: {res.text}")
    except Exception as e:
        logger.error(f"[ERROR] Connection error while loading {model_identifier}: {e}")

# ---------------------------------------------------------
# GRAPH NODES
# ---------------------------------------------------------
# ---------------------------------------------------------
# OPTIMIZED GRAPH NODES (No redundant Worker reloads)
# ---------------------------------------------------------
def planner_node(state: PlatformState):
    logger.info("=== [NODE: PLANNER] Loading Planner Model ===")
    load_model(PLANNER_MODEL_ID)
    
    planner_llm = ChatOpenAI(base_url=BASE_URL, api_key="lm-studio", model=PLANNER_MODEL_ID)
    system_prompt = SystemMessage(content=PLANNER_SYSTEM_PROMPT)
    
    response = planner_llm.invoke([system_prompt, HumanMessage(content=state["objective"])])
    plan_text = response.content.strip()
    
    if "```json" in plan_text:
        plan_text = plan_text.split("```json")[1].split("```")[0].strip()
    elif "```" in plan_text:
        plan_text = plan_text.split("```")[1].split("```")[0].strip()
        
    try:
        tasks = json.loads(plan_text)
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON plan from planner output.")
        tasks = []

    logger.info(f"Planner generated {len(tasks)} tasks.")
    unload_model_by_identifier(PLANNER_MODEL_ID)
    
    # Pre-load the worker model *once* right after planner unloads, 
    # so it stays hot for all sequential worker tasks!
    load_model(WORKER_MODEL_ID)
    
    return {"tasks": tasks, "current_task_index": 0, "generated_files": {}}

def worker_node(state: PlatformState):
    # NOTICE: No load_model() or unload_model() here! It stays hot in VRAM.
    logger.info("=== [NODE: WORKER] Executing Task (Worker stays loaded) ===")
    
    worker_llm = ChatOpenAI(base_url=BASE_URL, api_key="lm-studio", model=WORKER_MODEL_ID)
    tasks = state["tasks"]
    index = state["current_task_index"]
    generated_files = dict(state["generated_files"])
    
    current_task = tasks[index]
    logger.info(f"Executing Step {current_task.get('step')}: {current_task.get('task_name')}")
            # Fresh context isolation: We only supply the System Prompt and THIS task's instructions.
    # The model has zero memory of previous tasks, achieving a clean slate instantly.
    system_prompt = SystemMessage(content=WORKER_SYSTEM_PROMPT)
    response = worker_llm.invoke([system_prompt, HumanMessage(content=current_task["instructions"])])
    code_output = response.content.strip()
    
    if "```python" in code_output:
        code_output = code_output.split("```python")[1].split("```")[0].strip()
    elif "```" in code_output:
        code_output = code_output.split("```")[1].split("```")[0].strip()
        
    filename = current_task.get("filename", f"script_{index}.py")
    filepath = os.path.join(WORKSPACE, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code_output)
        
    logger.info(f"Worker saved code to {filepath}")
    generated_files[filename] = code_output
    
    return {
        "generated_files": generated_files,
        "current_task_index": index + 1
    }

def worker_router(state: PlatformState):
    if state["current_task_index"] < len(state["tasks"]):
        return "worker"
    
    # All tasks are done! Now we safely unload the worker model before moving to verifier.
    unload_model_by_identifier(WORKER_MODEL_ID)
    return "verifier"

def verifier_node(state: PlatformState):
    logger.info("=== [NODE: VERIFIER] Reloading Planner Model for Code Review ===")
    load_model(PLANNER_MODEL_ID)
    
    verifier_llm = ChatOpenAI(base_url=BASE_URL, api_key="lm-studio", model=PLANNER_MODEL_ID)
    code_summary = "\n\n".join([f"--- FILE: {name} ---\n{code}" for name, code in state["generated_files"].items()])
    
    system_prompt = SystemMessage(content=VERIFIER_SYSTEM_PROMPT)
    response = verifier_llm.invoke([system_prompt, HumanMessage(content=code_summary)])
    verdict = response.content.strip()
    
    logger.info(f"Verification complete. Verdict:\n{verdict[:300]}...")
    unload_model_by_identifier(PLANNER_MODEL_ID)
    
    return {"verification_report": verdict}

# ---------------------------------------------------------
# BUILD LANGGRAPH WORKFLOW
# ---------------------------------------------------------
workflow = StateGraph(PlatformState)

workflow.add_node("planner", planner_node)
workflow.add_node("worker", worker_node)
workflow.add_node("verifier", verifier_node)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "worker")
workflow.add_conditional_edges("worker", worker_router, {"worker": "worker", "verifier": "verifier"})
workflow.add_edge("verifier", END)

app = workflow.compile()

# ---------------------------------------------------------
# EXECUTION ENTRYPOINT
# ---------------------------------------------------------
if __name__ == "__main__":
    objective = OBJECTIVE
    
    logger.info("=== INITIALIZING PIPELINE ===")
    unload_all_models()
    
    initial_state = {
        "objective": objective,
        "tasks": [],
        "current_task_index": 0,
        "generated_files": {},
        "verification_report": ""
    }
    
    for event in app.stream(initial_state):
        for node_name, state_update in event.items():
            logger.info(f"Finished execution node -> [{node_name.upper()}]")
            
    logger.info("=== PIPELINE EXECUTION COMPLETE ===")
    print(f"\n[INFO] All execution logs saved timewise to {LOG_FILE}")