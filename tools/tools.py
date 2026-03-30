# bad ids list
# normally from a db
fraud_db = {
    100001: 0.9,  # High risk
    100002: 0.3,  # Medium risk
    100003: 0.8,  # High risk
}

def lookup_fraud_watchlist(sk_id: int) -> float:
    # get the fraud score for this id
    # Return the score from the database if present, otherwise default to 0.1
    return fraud_db.get(sk_id, 0.1)

def compute_alt_credit_score(data: dict) -> dict:
    # figure out alt credit score
    # Extract required fields
    income = data.get('AMT_INCOME_TOTAL', 0)
    credit = data.get('AMT_CREDIT', 1)  # Avoid division by zero

    # Compute ratio
    income_credit_ratio = income / credit if credit > 0 else 0

    # Compute alt credit score: higher ratio = higher score, capped at 1.0
    alt_credit_score = min(1.0, income_credit_ratio)

    return {
        "alt_credit_score": alt_credit_score,
        "income_credit_ratio": income_credit_ratio
    }