import os
import subprocess
import requests
import re
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config import (
    WORKSPACE,
    PLAN_FILE,
    CODE_FILE,
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
# 1. PLANNER: Handles multi-file breakdown
# ---------------------------------------------------------
def run_planner(objective: str):
    print("\n==============================================")
    print("PHASE 1: PLANNER EXECUTION")
    print("==============================================")
    load_model(PLANNER_MODEL_ID)
    
    planner_llm = ChatOpenAI(base_url=BASE_URL, api_key="lm-studio", model=PLANNER_MODEL_ID)
    
    system_prompt = SystemMessage(content=(
        "You are a Lead AI Architect. Break down the user's objective into an execution plan "
        "specifying multiple scripts if necessary (e.g. A.py and B.py). "
        "Output valid JSON matching: "
        '{"files_to_create": ["A.py", "B.py"], "instructions": "detailed steps for worker"}'
    ))
    
    response = planner_llm.invoke([system_prompt, HumanMessage(content=objective)])
    plan_text = response.content.strip()
    
    if "```json" in plan_text:
        plan_text = plan_text.split("```json")[1].split("```")[0].strip()
    elif "```" in plan_text:
        plan_text = plan_text.split("```")[1].split("```")[0].strip()
        
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        f.write(plan_text)
        
    print(f"[SUCCESS] Plan saved to {PLAN_FILE}")
    unload_model_by_identifier(PLANNER_MODEL_ID)

# ---------------------------------------------------------
# 2. WORKER: Synthesizes multiple files via text parsing
# ---------------------------------------------------------
def run_worker():
    print("\n==============================================")
    print("PHASE 2: WORKER MULTI-FILE GENERATION")
    print("==============================================")
    load_model(WORKER_MODEL_ID)
    
    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        plan = f.read()
        
    worker_llm = ChatOpenAI(base_url=BASE_URL, api_key="lm-studio", model=WORKER_MODEL_ID)
    
    system_prompt = SystemMessage(content=(
        "You are an expert Python Developer. Read the execution plan and write the requested Python scripts. "
        "To output multiple files, clearly demarcate each file using this exact header format before the code block:\n"
        "### FILE: filename.py\n"
        "```python\n# code here\n```\n"
        "Ensure script B executes script A to capture its output for naming the new file dynamically."
    ))
    
    response = worker_llm.invoke([system_prompt, HumanMessage(content=f"Plan:\n{plan}")])
    raw_output = response.content
    
    # Parse out individual files based on the header format
    file_matches = re.findall(r"### FILE:\s*([^\n]+)\s*```python(.*?)```", raw_output, re.DOTALL)
    
    if file_matches:
        for filename, code in file_matches:
            clean_name = filename.strip()
            clean_code = code.strip()
            filepath = os.path.join(WORKSPACE, clean_name)
            with open(filepath, "w", encoding="utf-8") as out_f:
                out_f.write(clean_code)
            print(f"[SUCCESS] Created file: {filepath}")
    else:
        # Fallback if it only output one standard code block
        with open(CODE_FILE, "w", encoding="utf-8") as f:
            f.write(raw_output)
        print(f"[WARNING] Fallback single file written to {CODE_FILE}")
        
    unload_model_by_identifier(WORKER_MODEL_ID)

# ---------------------------------------------------------
# 3. VERIFIER / TEST RUNNER
# ---------------------------------------------------------
def run_verifier():
    print("\n==============================================")
    print("PHASE 3: SANDBOX EXECUTION & VERIFICATION")
    print("==============================================")
    
    # Run B.py if it exists to test the dynamic file generation loop
    target_script = os.path.join(WORKSPACE, "B.py")
    if not os.path.exists(target_script):
        # Look for any generated python file as fallback
        py_files = [f for f in os.listdir(WORKSPACE) if f.endswith(".py") and f != "generated_tool.py"]
        if py_files:
            target_script = os.path.join(WORKSPACE, py_files[-1])

    if os.path.exists(target_script):
        print(f"[RUNNING] Executing {target_script} in sandbox...")
        try:
            result = subprocess.run(["python", target_script], cwd=WORKSPACE, capture_output=True, text=True, timeout=5)
            print(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")
            else:
                print("[SUCCESS] Script executed successfully. Check your sandbox folder for the dynamic file!")
        except Exception as e:
            print(f"[ERROR] Execution failed: {e}")
    else:
        print("[ERROR] No executable script found in sandbox.")

if __name__ == "__main__":
    objective = OBJECTIVE

    unload_all_models()
    run_planner(objective)
    run_worker()
    run_verifier()
    
    print("\n[PIPELINE COMPLETE]")