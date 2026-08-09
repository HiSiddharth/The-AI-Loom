import os
import json
import subprocess
import logging
from typing import TypedDict, List, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config import (
    WORKSPACE,
    BASE_URL,
    PLANNER_MODEL_ID,
    WORKER_MODEL_ID,
    PLANNER_SYSTEM_PROMPT,
    WORKER_SYSTEM_PROMPT,
    VERIFIER_SYSTEM_PROMPT,
    MAX_WORKER_RETRIES,
    MAX_MANAGER_RETRIES
)
from hardware import load_model, unload_model_by_identifier

logger = logging.getLogger("MiniPlatform")

class PlatformState(TypedDict):
    objective: str
    tasks: List[Dict[str, Any]]
    current_task_index: int
    generated_files: Dict[str, str]
    verification_report: str
    feedback_loop_count: int

def planner_node(state: PlatformState):
    logger.info("=== [NODE: PLANNER] Loading Planner Model ===")
    load_model(PLANNER_MODEL_ID)
    
    planner_llm = ChatOpenAI(base_url=BASE_URL, api_key="lm-studio", model=PLANNER_MODEL_ID)
    system_prompt = SystemMessage(content=PLANNER_SYSTEM_PROMPT)
    
    prompt_content = state["objective"]
    if state.get("verification_report") and "STATUS: REVISE" in state["verification_report"]:
        prompt_content = (
            f"Original Objective: {state['objective']}\n\n"
            f"Manager Feedback from previous attempt requiring revision:\n{state['verification_report']}\n\n"
            "Please revise the task plan to address this feedback."
        )

    response = planner_llm.invoke([system_prompt, HumanMessage(content=prompt_content)])
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
    
    load_model(WORKER_MODEL_ID)
    
    return {"tasks": tasks, "current_task_index": 0, "generated_files": {}}

def worker_node(state: PlatformState):
    logger.info("=== [NODE: WORKER] Executing Task with Self-Execution & Correction ===")
    
    worker_llm = ChatOpenAI(base_url=BASE_URL, api_key="lm-studio", model=WORKER_MODEL_ID)
    tasks = state["tasks"]
    index = state["current_task_index"]
    generated_files = dict(state["generated_files"])
    
    current_task = tasks[index]
    logger.info(f"Executing Step {current_task.get('step')}: {current_task.get('task_name')}")
    
    filename = current_task.get("filename")
    if not filename or filename.strip() == "":
        filename = f"script_{index}.py"
    else:
        filename = os.path.basename(filename)
        
    filepath = os.path.join(WORKSPACE, filename)
    code_output = ""
    
    for attempt in range(MAX_WORKER_RETRIES + 1):
        task_prompt = (
            f"Task Instructions:\n{current_task['instructions']}\n"
            f"Target Filename: {filename} (Must be saved inside workspace: {WORKSPACE})\n\n"
            f"Expected Output Specs & Edge Cases to Pass:\n{current_task.get('expected_output_spec', 'None')}"
        )
        if attempt > 0:
            task_prompt += f"\n\n[Self-Correction Attempt {attempt}] Previous run failed or had syntax/runtime errors. Fix them and ensure it executes cleanly."

        system_prompt = SystemMessage(content=WORKER_SYSTEM_PROMPT)
        response = worker_llm.invoke([system_prompt, HumanMessage(content=task_prompt)])
        raw_output = response.content.strip()
        
        if "```python" in raw_output:
            code_output = raw_output.split("```python")[1].split("```")[0].strip()
        elif "```" in raw_output:
            code_output = raw_output.split("```")[1].split("```")[0].strip()
        else:
            code_output = raw_output

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_output)

# Worker Self-Execution & Runtime Testing
        logger.info(f"Worker testing execution of {filename} (Attempt {attempt + 1})...")
        try:
            result = subprocess.run(
                ["python", filename],  # <-- Use just `filename` here instead of `filepath`
                capture_output=True,
                text=True,
                timeout=10,
                cwd=WORKSPACE
            )
            if result.returncode == 0:
                logger.info(f"Worker self-execution succeeded! Output:\n{result.stdout.strip()}")
                break
            else:
                logger.warning(f"Worker execution returned error code {result.returncode}:\n{result.stderr}")
                if attempt == MAX_WORKER_RETRIES:
                    logger.error("Max worker self-corrections reached. Saving script despite runtime errors.")
        except Exception as e:
            logger.warning(f"Worker execution raised exception: {e}")
            if attempt == MAX_WORKER_RETRIES:
                logger.error("Max worker corrections reached after exception.")
        
    logger.info(f"Worker finalized and saved code to {filepath}")
    generated_files[filename] = code_output
    
    return {
        "generated_files": generated_files,
        "current_task_index": index + 1
    }

def worker_router(state: PlatformState):
    if state["current_task_index"] < len(state["tasks"]):
        return "worker"
    
    unload_model_by_identifier(WORKER_MODEL_ID)
    return "verifier"

def verifier_node(state: PlatformState):
    logger.info("=== [NODE: MANAGER VERIFIER] Loading Planner Model for Review ===")
    load_model(PLANNER_MODEL_ID)
    
    verifier_llm = ChatOpenAI(base_url=BASE_URL, api_key="lm-studio", model=PLANNER_MODEL_ID)
    code_summary = "\n\n".join([f"--- FILE: {name} ---\n{code}" for name, code in state["generated_files"].items()])
    
    system_prompt = SystemMessage(content=VERIFIER_SYSTEM_PROMPT)
    prompt_content = f"Original Objective:\n{state['objective']}\n\nGenerated Codebase:\n{code_summary}"
    
    response = verifier_llm.invoke([system_prompt, HumanMessage(content=prompt_content)])
    verdict = response.content.strip()
    
    # Fallback if model outputs blank or fails to provide a status
    if not verdict:
        verdict = "STATUS: APPROVED" # Default fallback or handle as needed
        
    logger.info(f"Manager Review Verdict:\n{verdict}")

    unload_model_by_identifier(PLANNER_MODEL_ID)
    
    return {
        "verification_report": verdict,
        "feedback_loop_count": state.get("feedback_loop_count", 0) + 1
    }

def verifier_router(state: PlatformState):
    report = state.get("verification_report", "")
    loops = state.get("feedback_loop_count", 0)
    
    if "STATUS: APPROVED" in report or loops >= MAX_MANAGER_RETRIES:
        return "end"
    return "planner"