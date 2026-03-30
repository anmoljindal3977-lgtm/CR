from agents.risk_model import predict_risk

def main():
    test_data = {
        "AMT_CREDIT": 400000,
        "AMT_INCOME_TOTAL": 250000,
        "AMT_ANNUITY": 20000,
        "DAYS_BIRTH": -16000,
        "DAYS_EMPLOYED": -3000,
        "EXT_SOURCE_1": 0.5,
        "EXT_SOURCE_2": 0.5,
        "EXT_SOURCE_3": 0.5
    }

    result = predict_risk(test_data)

    print("\nRisk Output:")
    print(result)

if __name__ == "__main__":
    main()