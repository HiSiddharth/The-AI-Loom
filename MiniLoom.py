import os
import subprocess
import requests
import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config import (
    WORKSPACE,
    PLAN_FILE,
    VERDICT_FILE,
    LM_STUDIO_HOST,
    BASE_URL,
    PLANNER_MODEL_ID,
    WORKER_MODEL_ID, 
    OBJECTIVE
)

# ---------------------------------------------------------
# LM STUDIO HARDWARE MANAGEMENT HELPERS
# ---------------------------------------------------------
def unload_all_models():
    print("\n[VRAM MANAGER] Clearing all models from memory...")
    try:
        res = requests.get(f"{LM_STUDIO_HOST}/api/v0/models")
        if res.status_code == 200:
            for m in res.json().get("data", []):
                if instance_id := m.get("id"):
                    requests.post(f"{LM_STUDIO_HOST}/api/v1/models/unload", json={"instance_id": instance_id})
        print("[SUCCESS] VRAM completely cleared.")
    except Exception as e:
        print(f"[WARNING] Unload skipped: {e}")

def unload_model_by_identifier(model_identifier):
    print(f"\n[VRAM MANAGER] Unloading model: {model_identifier}...")
    try:
        res = requests.get(f"{LM_STUDIO_HOST}/api/v0/models")
        if res.status_code == 200:
            for m in res.json().get("data", []):
                if model_identifier in m.get("id", "") or model_identifier in m.get("identifier", ""):
                    requests.post(f"{LM_STUDIO_HOST}/api/v1/models/unload", json={"instance_id": m.get("id")})
                    return
        requests.post(f"{LM_STUDIO_HOST}/api/v1/models/unload", json={"model": model_identifier})
    except Exception as e:
        print(f"[WARNING] Selective unload error: {e}")

def load_model(model_identifier):
    print(f"\n[VRAM MANAGER] Loading model into VRAM: {model_identifier}...")
    try:
        res = requests.post(f"{LM_STUDIO_HOST}/api/v1/models/load", json={"model": model_identifier, "flash_attention": True})
        if res.status_code == 200:
            print(f"[SUCCESS] Loaded {model_identifier}")
        else:
            print(f"[ERROR] Load failed: {res.text}")
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")

# ---------------------------------------------------------
# 1. PLANNER: Pure Architecture & Task Breakdown (No Implementation)
# ---------------------------------------------------------
def run_planner(objective: str):
    print("\n==============================================")
    print("PHASE 1: PLANNER (Generating Sequential Task List)")
    print("==============================================")
    load_model(PLANNER_MODEL_ID)
    
    planner_llm = ChatOpenAI(base_url=BASE_URL, api_key="lm-studio", model=PLANNER_MODEL_ID)
    
    system_prompt = SystemMessage(content=(
        "You are a Lead AI Architect. Your job is purely to plan and break down the objective "
        "into an ordered sequence of granular implementation tasks for a developer worker. "
        "Do NOT write code implementations yourself. "
        "Output ONLY a valid JSON array of tasks matching this structure:\n"
        "[\n"
        '  {"step": 1, "task_name": "Create A.py", "instructions": "Write a python script A.py that prints the fibonacci series."},\n'
        '  {"step": 2, "task_name": "Create B.py", "instructions": "Write a python script B.py that executes A.py, captures its output, and creates a new file named after that output containing a copy of A.py."}\n'
        "]"
    ))
    
    response = planner_llm.invoke([system_prompt, HumanMessage(content=objective)])
    plan_text = response.content.strip()
    
    # Extract JSON block safely
    if "```json" in plan_text:
        plan_text = plan_text.split("```json")[1].split("```")[0].strip()
    elif "```" in plan_text:
        plan_text = plan_text.split("```")[1].split("```")[0].strip()
        
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        f.write(plan_text)
        
    print(f"[SUCCESS] Sequential plan saved to {PLAN_FILE}")
    unload_model_by_identifier(PLANNER_MODEL_ID)

# ---------------------------------------------------------
# 2. WORKER: Executes Tasks One-by-One Sequentially
# ---------------------------------------------------------
def run_worker_tasks():
    print("\n==============================================")
    print("PHASE 2: WORKER (Executing Tasks Sequentially)")
    print("==============================================")
    
    if not os.path.exists(PLAN_FILE):
        raise FileNotFoundError("Execution plan not found!")
        
    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    # Load worker model once for the sequence
    load_model(WORKER_MODEL_ID)
    worker_llm = ChatOpenAI(base_url=BASE_URL, api_key="lm-studio", model=WORKER_MODEL_ID)
    
    for item in tasks:
        step_num = item.get("step")
        task_name = item.get("task_name")
        instructions = item.get("instructions")
        
        print(f"\n--- Running Step {step_num}: {task_name} ---")
        
        system_prompt = SystemMessage(content=(
            "You are an expert execution Software Engineer. Read the specific task instructions provided, "
            "and write the requested complete, functional Python code file. "
            "Output ONLY raw Python code inside a markdown block. Do not include extraneous text."
        ))
        
        response = worker_llm.invoke([system_prompt, HumanMessage(content=instructions)])
        code_output = response.content.strip()
        
        # Clean markdown code block
        if "```python" in code_output:
            code_output = code_output.split("```python")[1].split("```")[0].strip()
        elif "```" in code_output:
            code_output = code_output.split("```")[1].split("```")[0].strip()
            
        # Determine filename dynamically based on task info or fallback
        filename = "A.py" if "A.py" in task_name or "A.py" in instructions else "B.py"
        if "B.py" in task_name or "B.py" in instructions:
            filename = "B.py"
            
        filepath = os.path.join(WORKSPACE, filename)
        with open(filepath, "w", encoding="utf-8") as code_file:
            code_file.write(code_output)
            
        print(f"[SUCCESS] Task {step_num} completed. Saved to {filepath}")

    unload_model_by_identifier(WORKER_MODEL_ID)

# ---------------------------------------------------------
# 3. VERIFIER / TEST RUNNER
# ---------------------------------------------------------
def run_verifier():
    print("\n==============================================")
    print("PHASE 3: SANDBOX EXECUTION & TESTING")
    print("==============================================")
    
    target_script = os.path.join(WORKSPACE, "B.py")
    if os.path.exists(target_script):
        print(f"[RUNNING] Executing B.py in sandbox...")
        try:
            result = subprocess.run(["python", target_script], cwd=WORKSPACE, capture_output=True, text=True, timeout=5)
            print(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")
            else:
                print("[SUCCESS] Script executed successfully. Check your sandbox folder for the generated file!")
        except Exception as e:
            print(f"[ERROR] Execution failed: {e}")
    else:
        print("[ERROR] B.py not found in sandbox.")

if __name__ == "__main__":
    objective = OBJECTIVE
    
    unload_all_models()
    run_planner(objective)
    run_worker_tasks()
    run_verifier()
    
    print("\n[PIPELINE COMPLETE]")