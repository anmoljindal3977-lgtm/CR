def make_decision(risk: dict, alt_credit: dict) -> dict:
    p_default = risk['p_default']
    alt_credit_score = alt_credit['alt_credit_score']

    if p_default < 0.05 and alt_credit_score > 0.6:
        # low risk so approve
        decision = "APPROVE"
        reason = "Low default probability and good alternative credit score"
    elif p_default > 0.2:
        # high risk so reject
        decision = "REJECT"
        reason = "High default probability"
    else:
        # unsure → manual review
        decision = "MANUAL_REVIEW"
        reason = "Moderate risk, requires manual review"

    return {
        "decision": decision,
        "reason": reason
    }