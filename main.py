import time
import argparse
import logging
from config import LOG_FILE, OBJECTIVE
from hardware import unload_all_models
from graph import build_workflow
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MiniPlatform")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Loom - Local Multi-Model Coding Orchestrator")
    parser.add_argument("-o", "--objective", type=str, default=OBJECTIVE, help="Coding objective for the agent pipeline")
    args = parser.parse_args()

    start_time = time.perf_counter()
    logger.info("=== INITIALIZING AI-LOOM PLATFORM ===")
    logger.info(f"Objective: {args.objective}")
    unload_all_models()
    
    app = build_workflow()
    
    initial_state = {
        "objective": args.objective,
        "tasks": [],
        "current_task_index": 0,
        "generated_files": {},
        "execution_results": {},
        "verification_report": "",
        "feedback_loop_count": 0
    }
    
    for event in app.stream(initial_state):
        for node_name, state_update in event.items():
            logger.info(f"Finished execution node -> [{node_name.upper()}]")

    total_time = time.perf_counter() - start_time
    logger.info(f"=== PIPELINE EXECUTION COMPLETE in {total_time:.2f}s ===")
    print(f"\n[INFO] Pipeline finished in {total_time:.2f}s. Logs saved to {LOG_FILE}")