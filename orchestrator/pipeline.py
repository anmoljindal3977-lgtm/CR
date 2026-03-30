from agents.data_validator import validate_application
from agents.alt_credit import generate_alt_credit
from agents.risk_model import predict_risk
from agents.decision_engine import make_decision
from orchestrator.explanation import generate_explanation

def run_pipeline(data: dict) -> dict:
    # checking validation first
    validator_output = validate_application(data)
    if validator_output["status"] == "FAIL":
        # stopping if invalid
        return {"validator": validator_output}

    # running rest of pipeline
    alt_credit_output = generate_alt_credit(data)
    risk_output = predict_risk(data)
    decision_output = make_decision(risk_output, alt_credit_output)

    return {
        "validator": validator_output,
        "alt_credit": alt_credit_output,
        "risk": risk_output,
        "decision": decision_output
    }