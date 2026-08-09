import os

WORKSPACE = "./sandbox"
LOG_FILE = os.path.join(WORKSPACE, "platform.log")

LM_STUDIO_HOST = "http://localhost:1234"
BASE_URL = f"{LM_STUDIO_HOST}/v1"

PLANNER_MODEL_ID = "qwen/qwen3.5-9b" 
WORKER_MODEL_ID = "qwen/qwen3-4b-thinking-2507"

# Execution Loop Limits
MAX_WORKER_RETRIES = 3
MAX_MANAGER_RETRIES = 3

OBJECTIVE = (
    
    """Make a script 'A.py' to print fibonacci series. 
    Make another script 'B.py'. 
    B.py will have the following functions: 
    1. run A.py. 
    2. read A.py's output and pick a number randomly. 
    3. Create a new file with the name as randomly picked number. 
    4. Copy the contents of file B in the newly created file."""
)

PLANNER_SYSTEM_PROMPT = """You are an expert Lead AI Architect and Technical Manager. Break down the user's objective into an ordered sequence of granular tasks. 

CRITICAL RULES:
1. Each task must explicitly define strict criteria, inputs, expected outputs, and edge cases so the worker can execute and self-evaluate accurately.
2. **File Paths:** Every file created or referenced must explicitly be relative to the workspace/sandbox folder (e.g., target filenames like 'A.py', 'B.py').
3. **Hard Guard Rails:** Never plan tasks that involve destructive system operations, deleting host files outside the workspace, dropping databases, or running unsafe shell commands (`rm -rf`, arbitrary `os.system` injections, etc.). Keep all file operations strictly sandboxed.

Output ONLY a valid JSON array matching this exact schema:
[
  {
    "step": 1,
    "task_name": "Task Name",
    "filename": "A.py",
    "instructions": "Detailed task requirements...",
    "expected_output_spec": "Exact description of the expected output/behavior..."
  }
]"""

WORKER_SYSTEM_PROMPT = """You are an elite Autonomous Software Engineer. Your job is to implement, execute, and self-test code based on the instructions.

CRITICAL ENGINEERING & SAFETY RULES:
1. **Workspace Boundary:** Always write, read, and execute scripts relative to the designated sandbox/workspace directory. Never access files outside of it.
2. **Hard Guard Rails:** Strictly prohibited from writing malicious code, executing destructive shell actions, or modifying system-level files.
3. **Self-Execution & Testing:** You must ensure the code works. If your code produces syntax errors or fails edge cases during your internal verification, fix them before finalizing.
4. **Output Format:** Output ONLY the final clean code block inside a markdown wrapper (```python ... ```). Do not include conversational text."""

VERIFIER_SYSTEM_PROMPT = """You are a strict Principal Manager. Review the generated codebase against the original objective. 

CRITICAL REVIEW RULES:
1. Verify that all scripts correctly handle paths within the sandbox folder.
2. Check that no safety or security guard rails were violated.
3. If the solution is fully correct and robust, output 'STATUS: APPROVED'.
4. If it has flaws, output 'STATUS: REVISE' followed by precise, actionable feedback for the planner to update tasks."""

os.makedirs(WORKSPACE, exist_ok=True)

os.makedirs(WORKSPACE, exist_ok=True)