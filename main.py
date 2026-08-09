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
    logger.info("=== INITIALIZING AI-LOOM PLATFORM ===")
    unload_all_models()
    
    app = build_workflow()
    
    initial_state = {
        "objective": OBJECTIVE,
        "tasks": [],
        "current_task_index": 0,
        "generated_files": {},
        "verification_report": "",
        "feedback_loop_count": 0
    }
    
    for event in app.stream(initial_state):
        for node_name, state_update in event.items():
            logger.info(f"Finished execution node -> [{node_name.upper()}]")
            
    logger.info("=== PIPELINE EXECUTION COMPLETE ===")
    print(f"\n[INFO] All execution logs saved timewise to {LOG_FILE}")