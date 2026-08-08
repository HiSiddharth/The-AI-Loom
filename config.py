import os

# Configuration Paths
WORKSPACE = "./sandbox"
LOG_FILE = os.path.join(WORKSPACE, "platform.log")

# LM Studio Native Management & Inference Endpoints
LM_STUDIO_HOST = "http://localhost:1234"
BASE_URL = f"{LM_STUDIO_HOST}/v1"

# Model Identifiers
PLANNER_MODEL_ID = "mn-violet-lotus-12b" 
WORKER_MODEL_ID = "qwen/qwen3-4b-thinking-2507"

# ---------------------------------------------------------
# SYSTEM PROMPTS CONFIGURATION
# ---------------------------------------------------------
PLANNER_SYSTEM_PROMPT = (
    "You are a Lead AI Architect. Break down the user's objective into an ordered sequence "
    "of granular implementation tasks for a worker. "
    "Output ONLY a valid JSON array of tasks matching this structure:\n"
    "[\n"
    '  {"step": 1, "task_name": "Create A.py", "filename": "A.py", "instructions": "Write script A.py..."},\n'
    '  {"step": 2, "task_name": "Create B.py", "filename": "B.py", "instructions": "Write script B.py..."}\n'
    "]"
)

WORKER_SYSTEM_PROMPT = (
    "You are an expert execution Software Engineer. Read the specific task instructions, "
    "and write the requested complete, functional Python code file. "
    "CRITICAL RULE: When your scripts need to read or write other files (like other scripts in the sandbox), "
    "always use paths relative to the script's own directory using 'os.path.dirname(__file__)' "
    "so they execute correctly regardless of the current working directory. "
    "Output ONLY raw Python code inside a markdown code block."
)

VERIFIER_SYSTEM_PROMPT = (
    "You are a rigorous Principal Code Reviewer. Inspect the provided Python scripts "
    "for logic errors, missing edge cases, or runtime failures based on the initial objective. "
    "Provide a final review summary and verdict."
)

OBJECTIVE = (
        "Make a script 'A.py' to print fibonacci series, and then another script 'B.py' "
        "to create a new file and copy contents of script A.py onto a new file named randomly "
        "from the output of the script A on running it first time."
    )

os.makedirs(WORKSPACE, exist_ok=True)