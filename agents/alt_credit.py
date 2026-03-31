"""
This file calculates alternative credit scores.
"""

from tools.tools import compute_alt_credit_score

def generate_alt_credit(data: dict) -> dict:
    """
    Gets alternative credit score from tool.
    """
    # calling tool to get score
    result = compute_alt_credit_score(data)

    # get the values
    alt_credit_score = result['alt_credit_score']
    income_credit_ratio = result['income_credit_ratio']

    # simple comment
    comment = "score based on how much income compared to credit amount"

    return {
        "alt_credit_score": alt_credit_score,
        "income_credit_ratio": income_credit_ratio,
        "comment": comment
    }