"""
This file runs the full credit risk pipeline.
"""

from agents.data_validator import validate_application
from agents.alt_credit import generate_alt_credit
from agents.risk_model import predict_risk
from agents.decision_engine import make_decision

def run_pipeline(data: dict) -> dict:
    """
    Runs validation, alt credit, risk, and decision agents in order.
    """
    trace = []
    
    # checking validation first
    validator_output = validate_application(data)
    trace.append({"step": "validator", "output": validator_output})
    
    if validator_output["status"] == "FAIL":
        # stopping if invalid
        result = {"validator": validator_output}
        result["trace"] = trace
        return result

    # running rest of pipeline
    alt_credit_output = generate_alt_credit(data)
    trace.append({"step": "alt_credit", "output": alt_credit_output})
    
    risk_output = predict_risk(data)
    trace.append({"step": "risk", "output": risk_output})
    
    decision_output = make_decision(risk_output, alt_credit_output)
    
    if decision_output["decision"] == "MANUAL_REVIEW":
        print("Manual review required. Approve? (y/n)")
        user_input = input().strip().lower()
        if user_input == "y":
            decision_output["decision"] = "APPROVE"
            decision_output["reason"] = "Approved after manual review"
        elif user_input == "n":
            decision_output["decision"] = "REJECT"
            decision_output["reason"] = "Rejected after manual review"
        # else keep as MANUAL_REVIEW
    
    trace.append({"step": "decision", "output": decision_output})

    result = {
        "validator": validator_output,
        "alt_credit": alt_credit_output,
        "risk": risk_output,
        "decision": decision_output
    }
    result["trace"] = trace
    return result