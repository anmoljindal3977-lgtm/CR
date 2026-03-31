"""
This file runs the full credit risk pipeline.
"""

import os
import json
from agents.data_validator import validate_application
from agents.alt_credit import generate_alt_credit
from agents.risk_model import predict_risk
from agents.decision_engine import make_decision
from orchestrator.explanation import generate_explanation


def run_pipeline(data: dict, interactive: bool = True, manual_override: str = None) -> dict:
    """
    Runs validation, alt credit, risk, decision, and explanation in order.
    """
    trace = []

    # checking validation first
    validator_output = validate_application(data)
    trace.append({"step": "validator", "output": validator_output})

    if validator_output["status"] == "FAIL":
        result = {
            "validator": validator_output,
            "alt_credit": None,
            "risk": None,
            "decision": {
                "decision": "INVALID",
                "reason": validator_output.get("reason", "Validation failed")
            }
        }
        explanation_text = generate_explanation(result)
        trace.append({"step": "explanation", "output": explanation_text})
        result["explanation"] = explanation_text
        result["trace"] = trace
        return result

    # running rest of pipeline
    alt_credit_output = generate_alt_credit(data)
    trace.append({"step": "alt_credit", "output": alt_credit_output})

    risk_output = predict_risk(data)
    trace.append({"step": "risk", "output": risk_output})

    decision_output = make_decision(risk_output, alt_credit_output)

    # human-in-the-loop for medium risk
    if decision_output["decision"] == "MANUAL_REVIEW":
        # provide review details for decision-maker
        review_details = {
            "risk_probability": risk_output.get("p_default"),
            "alt_credit_score": alt_credit_output.get("alt_credit_score"),
            "risk_comment": risk_output.get("comment"),
            "alt_credit_comment": alt_credit_output.get("comment"),
            "decision_reason": decision_output.get("reason")
        }
        decision_output["manual_review_details"] = review_details

        if manual_override is None:
            manual_override = os.getenv("MANUAL_REVIEW_OVERRIDE")

        if manual_override is not None:
            manual_override = manual_override.strip().lower()

        if interactive and manual_override is None:
            print("Manual review required, details:")
            print(json.dumps(review_details, indent=2))
            print("Approve? (y/n)")
            user_input = input().strip().lower()
            manual_override = user_input

        if manual_override == "y":
            decision_output["decision"] = "APPROVE"
            decision_output["reason"] = "Approved after manual review"
        elif manual_override == "n":
            decision_output["decision"] = "REJECT"
            decision_output["reason"] = "Rejected after manual review"
        else:
            decision_output["reason"] = "Manual review pending"

    trace.append({"step": "decision", "output": decision_output})

    # collect outputs before explanation
    result = {
        "validator": validator_output,
        "alt_credit": alt_credit_output,
        "risk": risk_output,
        "decision": decision_output
    }

    explanation_text = generate_explanation(result)
    trace.append({"step": "explanation", "output": explanation_text})
    result["explanation"] = explanation_text

    result["trace"] = trace
    return result