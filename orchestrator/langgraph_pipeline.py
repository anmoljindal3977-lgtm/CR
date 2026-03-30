"""
This file sets up the pipeline using LangGraph.
"""

from langgraph.graph import StateGraph
from agents.data_validator import validate_application
from agents.alt_credit import generate_alt_credit
from agents.risk_model import predict_risk
from agents.decision_engine import make_decision

# defining graph flow
graph = StateGraph(dict)

graph.add_node("validator", validate_application)
graph.add_node("alt_credit", generate_alt_credit)
graph.add_node("risk", predict_risk)
graph.add_node("decision", make_decision)

graph.set_entry_point("validator")

# handling validation failure
def check_validation(state):
    """
    Checks if validation passed or failed.
    """
    if state["validator"]["status"] == "FAIL":
        return "end"
    return "alt_credit"

graph.add_conditional_edges(
    "validator",
    check_validation,
    {
        "alt_credit": "alt_credit",
        "end": None
    }
)

# connecting agents
graph.add_edge("alt_credit", "risk")
graph.add_edge("risk", "decision")

app = graph.compile()

def run_langgraph_pipeline(data):
    """
    Runs the LangGraph pipeline with input data.
    """
    return app.invoke(data)