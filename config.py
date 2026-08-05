import os

## Task
OBJECTIVE =  ("Make a script 'A.py' to print fibonacci series, and then another script 'B.py' "
        "to create a new file and copy contents of script A.py onto a new file named randomly "
        "from the output of the script A on running it first time.")
# Configuration Paths
WORKSPACE = "./sandbox"
PLAN_FILE = os.path.join(WORKSPACE, "execution_plan.json")
CODE_FILE = os.path.join(WORKSPACE, "generated_tool.py")
VERDICT_FILE = os.path.join(WORKSPACE, "verification_report.md")

# LM Studio Native Management & Inference Endpoints
LM_STUDIO_HOST = "http://localhost:1234"
BASE_URL = f"{LM_STUDIO_HOST}/v1"

# Model Identifiers
PLANNER_MODEL_ID = "mn-violet-lotus-12b" 
WORKER_MODEL_ID = "qwen/qwen3-4b-thinking-2507"

# Ensure workspace directory exists
os.makedirs(WORKSPACE, exist_ok=True)