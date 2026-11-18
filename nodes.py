import os
import re
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
    execution_results: Dict[str, str]
    verification_report: str
    feedback_loop_count: int

def _strip_thinking(text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"<think>.*", "", cleaned, flags=re.DOTALL)
    return cleaned.strip()

def _extract_code_block(text: str, lang: str = "") -> str:
    cleaned = _strip_thinking(text)
    if lang and f"```{lang}" in cleaned:
        return cleaned.split(f"```{lang}", 1)[1].split("```", 1)[0].strip()
    if "```" in cleaned:
        return cleaned.split("```", 1)[1].split("```", 1)[0].strip()
    return cleaned

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

    tasks = []
    for attempt in range(2):
        response = planner_llm.invoke([system_prompt, HumanMessage(content=prompt_content)])
        plan_text = _extract_code_block(response.content, lang="json")
        try:
            parsed = json.loads(plan_text)
            if isinstance(parsed, list) and len(parsed) > 0:
                tasks = parsed
                break
            logger.warning(f"Planner returned empty or non-list JSON on attempt {attempt + 1}.")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON plan (attempt {attempt + 1}): {e}")
            prompt_content += "\n\nCRITICAL: Previous output was not valid JSON. Output ONLY a valid JSON array."

    logger.info(f"Planner generated {len(tasks)} tasks.")
    unload_model_by_identifier(PLANNER_MODEL_ID)
    
    if tasks:
        load_model(WORKER_MODEL_ID)
    else:
        logger.error("Planner failed to produce any valid tasks. Aborting workflow.")
    
    return {"tasks": tasks, "current_task_index": 0, "generated_files": {}, "execution_results": {}}

def planner_router(state: PlatformState):
    if not state.get("tasks"):
        return "end"
    return "worker"

def worker_node(state: PlatformState):
    logger.info("=== [NODE: WORKER] Executing Task with Self-Execution & Correction ===")
    
    worker_llm = ChatOpenAI(base_url=BASE_URL, api_key="lm-studio", model=WORKER_MODEL_ID)
    tasks = state["tasks"]
    index = state["current_task_index"]
    generated_files = dict(state["generated_files"])
    execution_results = dict(state.get("execution_results", {}))
    
    if index >= len(tasks):
        logger.warning("Worker called with no remaining tasks.")
        return {"current_task_index": index}

    current_task = tasks[index]
    logger.info(f"Executing Step {current_task.get('step')}: {current_task.get('task_name')}")
    
    filename = current_task.get("filename")
    if not filename or filename.strip() == "":
        filename = f"script_{index}.py"
    else:
        filename = os.path.basename(filename)
        
    filepath = os.path.join(WORKSPACE, filename)
    code_output = ""
    last_error = ""
    exec_summary = "Not executed"
    existing_files = ", ".join(generated_files.keys()) if generated_files else "None"
    
    for attempt in range(MAX_WORKER_RETRIES + 1):
        task_prompt = (
            f"Task Instructions:\n{current_task['instructions']}\n"
            f"Target Filename: {filename} (Working directory is already the workspace)\n"
            f"Existing files in workspace: {existing_files}\n\n"
            f"Expected Output Specs & Edge Cases to Pass:\n{current_task.get('expected_output_spec', 'None')}"
        )
        if attempt > 0:
            task_prompt += (
                f"\n\n[Self-Correction Attempt {attempt}] Your previous code failed.\n"
                f"--- PREVIOUS CODE ---\n```python\n{code_output}\n```\n"
                f"--- ERROR OUTPUT ---\n{last_error}\n\n"
                "Fix the root cause and output the complete corrected script."
            )

        system_prompt = SystemMessage(content=WORKER_SYSTEM_PROMPT)
        response = worker_llm.invoke([system_prompt, HumanMessage(content=task_prompt)])
        code_output = _extract_code_block(response.content, lang="python")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_output)

        logger.info(f"Worker testing execution of {filename} (Attempt {attempt + 1})...")
        try:
            result = subprocess.run(
                ["python", filename],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=WORKSPACE
            )
            if result.returncode == 0:
                stdout_preview = result.stdout.strip()
                logger.info(f"Worker self-execution succeeded! Output:\n{stdout_preview}")
                exec_summary = f"EXIT 0 | STDOUT:\n{stdout_preview[:1000]}"
                break
            else:
                last_error = f"Return code {result.returncode}\nSTDERR:\n{result.stderr.strip()}\nSTDOUT:\n{result.stdout.strip()}"
                exec_summary = f"EXIT {result.returncode} | {last_error[:1000]}"
                logger.warning(f"Worker execution failed:\n{last_error}")
                if attempt == MAX_WORKER_RETRIES:
                    logger.error("Max worker self-corrections reached. Saving script despite runtime errors.")
        except Exception as e:
            last_error = f"Execution exception: {e}"
            exec_summary = last_error
            logger.warning(f"Worker execution raised exception: {e}")
            if attempt == MAX_WORKER_RETRIES:
                logger.error("Max worker corrections reached after exception.")
        
    logger.info(f"Worker finalized and saved code to {filepath}")
    generated_files[filename] = code_output
    execution_results[filename] = exec_summary
    
    return {
        "generated_files": generated_files,
        "execution_results": execution_results,
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
    exec_results = state.get("execution_results", {})
    code_summary = "\n\n".join([
        f"--- FILE: {name} ---\n{code}\n\n[Execution Result]\n{exec_results.get(name, 'No execution recorded')}"
        for name, code in state["generated_files"].items()
    ])
    
    system_prompt = SystemMessage(content=VERIFIER_SYSTEM_PROMPT)
    prompt_content = f"Original Objective:\n{state['objective']}\n\nGenerated Codebase & Execution Results:\n{code_summary}"
    
    response = verifier_llm.invoke([system_prompt, HumanMessage(content=prompt_content)])
    verdict = _strip_thinking(response.content)
    
    # Fail closed if verifier produces empty output or omits a valid status
    if not verdict or ("STATUS: APPROVED" not in verdict and "STATUS: REVISE" not in verdict):
        verdict = f"STATUS: REVISE\nVerifier did not issue a clear approval. Raw output:\n{verdict or '[EMPTY]'}"
        
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