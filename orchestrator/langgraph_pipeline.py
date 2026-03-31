"""
This file sets up the pipeline using LangGraph.
"""

from orchestrator.pipeline import run_pipeline


def run_langgraph_pipeline(data, interactive=False, manual_override=None):
    """
    Runs the full pipeline with LangGraph-friendly interface.

    This wraps the orchestrator pipeline so that the NL graph path and explanation
    step are included consistently.
    """
    return run_pipeline(data, interactive=interactive, manual_override=manual_override)