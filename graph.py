import logging
from langgraph.graph import END, START, StateGraph

from nodes import (
    PlatformState,
    planner_node,
    planner_router,
    worker_node,
    worker_router,
    verifier_node,
    verifier_router
)

logger = logging.getLogger("MiniPlatform")

def build_workflow():
    workflow = StateGraph(PlatformState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("worker", worker_node)
    workflow.add_node("verifier", verifier_node)

    workflow.add_edge(START, "planner")
    workflow.add_conditional_edges("planner", planner_router, {"worker": "worker", "end": END})
    workflow.add_conditional_edges("worker", worker_router, {"worker": "worker", "verifier": "verifier"})
    workflow.add_conditional_edges("verifier", verifier_router, {"planner": "planner", "end": END})
    return workflow.compile()