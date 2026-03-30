"""
This file runs the main pipeline with test data.
"""

from orchestrator.langgraph_pipeline import run_langgraph_pipeline

def main():
    """
    Runs the pipeline with sample data and prints result.
    """
    # sample data for testing
    test_data = {
        "SK_ID_CURR": 100002,
        "AMT_CREDIT": 400000,
        "AMT_INCOME_TOTAL": 250000,
        "AMT_ANNUITY": 20000,
        "DAYS_BIRTH": -16000,
        "DAYS_EMPLOYED": -3000,
        "EXT_SOURCE_1": 0.5,
        "EXT_SOURCE_2": 0.5,
        "EXT_SOURCE_3": 0.5
    }

    result = run_langgraph_pipeline(test_data)
    print(result)

if __name__ == "__main__":
    main()