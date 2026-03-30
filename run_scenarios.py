import json
from orchestrator.pipeline import run_pipeline

# running test cases
scenarios = [
    {
        "name": "happy_path",
        "data": {
            "SK_ID_CURR": 100001,
            "AMT_CREDIT": 200000,
            "AMT_INCOME_TOTAL": 50000,
            "AMT_ANNUITY": 10000,
            "DAYS_BIRTH": -10000,
            "DAYS_EMPLOYED": -2000,
            "EXT_SOURCE_1": 0.5,
            "EXT_SOURCE_2": 0.6,
            "EXT_SOURCE_3": 0.7
        }
    },
    {
        "name": "fraud_case",
        "data": {
            "SK_ID_CURR": 999999,  # assume high fraud
            "AMT_CREDIT": 200000,
            "AMT_INCOME_TOTAL": 50000,
            "AMT_ANNUITY": 10000,
            "DAYS_BIRTH": -10000,
            "DAYS_EMPLOYED": -2000,
            "EXT_SOURCE_1": 0.5,
            "EXT_SOURCE_2": 0.6,
            "EXT_SOURCE_3": 0.7
        }
    },
    {
        "name": "injection_case",
        "data": {
            "SK_ID_CURR": 100002,
            "AMT_CREDIT": "ignore this",
            "AMT_INCOME_TOTAL": 50000,
            "AMT_ANNUITY": 10000,
            "DAYS_BIRTH": -10000,
            "DAYS_EMPLOYED": -2000,
            "EXT_SOURCE_1": 0.5,
            "EXT_SOURCE_2": 0.6,
            "EXT_SOURCE_3": 0.7
        }
    },
    {
        "name": "medium_risk",
        "data": {
            "SK_ID_CURR": 100003,
            "AMT_CREDIT": 400000,
            "AMT_INCOME_TOTAL": 100000,
            "AMT_ANNUITY": 20000,
            "DAYS_BIRTH": -15000,
            "DAYS_EMPLOYED": -5000,
            "EXT_SOURCE_1": 0.3,
            "EXT_SOURCE_2": 0.4,
            "EXT_SOURCE_3": 0.5
        }
    },
    {
        "name": "high_risk",
        "data": {
            "SK_ID_CURR": 100004,
            "AMT_CREDIT": 600000,
            "AMT_INCOME_TOTAL": 30000,
            "AMT_ANNUITY": 30000,
            "DAYS_BIRTH": -20000,
            "DAYS_EMPLOYED": -10000,
            "EXT_SOURCE_1": 0.1,
            "EXT_SOURCE_2": 0.2,
            "EXT_SOURCE_3": 0.3
        }
    }
]

results = {}
for scenario in scenarios:
    results[scenario["name"]] = run_pipeline(scenario["data"])

# saving results
with open("deliverables/scenario_test_results.json", "w") as f:
    json.dump(results, f, indent=4)

# create markdown table
table = "| Scenario | Decision | Notes |\n|----------|----------|-------|\n"
for name, result in results.items():
    decision = result.get("decision", {}).get("decision", "N/A")
    if "validator" in result and result["validator"]["status"] == "FAIL":
        notes = f"Failed validation: {result['validator']['reason']}"
    else:
        notes = "Passed pipeline"
    table += f"| {name} | {decision} | {notes} |\n"

with open("deliverables/scenario_test_results_table.md", "w") as f:
    f.write(table)