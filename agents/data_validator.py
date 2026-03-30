from tools.tools import lookup_fraud_watchlist

def validate_application(data: dict) -> dict:
    # check the app data
    # check needed fields
    required_fields = ['SK_ID_CURR', 'AMT_CREDIT', 'AMT_INCOME_TOTAL']
    for field in required_fields:
        if field not in data:
            return {
                "status": "FAIL",
                "reason": f"Missing required field: {field}",
                "fraud_score": 0.0,
                "flags": []
            }

    # spot bad words
    injection_words = ["ignore", "override", "hack"]
    for key, value in data.items():
        if isinstance(value, str):
            for word in injection_words:
                if word.lower() in value.lower():
                    return {
                        "status": "FAIL",
                        "reason": "INJECTION_DETECTED",
                        "fraud_score": 0.0,
                        "flags": []
                    }

    # check if fraud
    sk_id = data['SK_ID_CURR']
    fraud_score = lookup_fraud_watchlist(sk_id)
    if fraud_score > 0.7:
        return {
            "status": "FAIL",
            "reason": "High fraud score",
            "fraud_score": fraud_score,
            "flags": []
        }

    # looks good
    return {
        "status": "PASS",
        "reason": "Validation passed",
        "fraud_score": fraud_score,
        "flags": []
    }