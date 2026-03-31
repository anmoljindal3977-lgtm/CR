# Final Design Document

## 1. Problem Statement
This project implements a credit risk decision pipeline with multi-agent architecture. It evaluates loan applications by combining fraud validation, alternate credit scoring, risk modeling, and a decision engine, with explainability powered by an LLM (Ollama llama3). The system supports human-in-the-loop for medium-risk cases.

## 2. Architecture
Flow:
- Input data → `run_pipeline()`
- `data_validator.validate_application`
- `alt_credit.generate_alt_credit`
- `risk_model.predict_risk`
- `decision_engine.make_decision`
- `explanation.generate_explanation` (Ollama llama3)
- output includes `validator`,`alt_credit`,`risk`,`decision`,`explanation`,`trace`

## 3. Agent descriptions
- validator: checks required fields, injection, fraud watchlist
- alt_credit: computes income/credit ratio and alt score
- risk: loads LightGBM model, predicts default probability
- decision: business rules -> APPROVE/REJECT/MANUAL_REVIEW
- explanation: LLM prompt from `prompts/explanation.md` via `ollama run llama3`

## 4. Tools used
- pandas, scikit-learn, lightgbm, joblib
- langgraph (for alternative pipeline path)
- ollama CLI (`ollama run llama3`, `ollama serve`, `ollama pull llama3`)

## 5. Guardrails
- Decision is deterministic from model and threshold rules
- LLM is only used for explanation, does not affect decision
- Manual override via `MANUAL_REVIEW_OVERRIDE` or interactive input

## 6. Orchestration pattern
- `orchestrator/pipeline.py` orchestrates calls and traces steps.
- `orchestrator/langgraph_pipeline.py` wraps pipeline entry point.

## 7. Scenario testing results
Stored in `deliverables/scenario_test_results.json` and `deliverables/scenario_test_results_table.md`.

## 8. Sub-agent evaluation
Script: `evaluation/evaluate_alt_credit.py`
- Uses 20 rows from `data/application_test.csv`
- Computes precision, recall, F1 via alt-credit threshold logic

## 9. Observability & tracing
- `trace` includes step outputs at each stage.
- `run_pipeline` returns a result containing `trace`.

## 10. Prompt engineering
Prompt is in `prompts/explanation.md` with role, task, input format, and examples.

## 11. Human-in-the-loop
- `decision_engine` returns `MANUAL_REVIEW` for moderate risk.
- `run_pipeline` supports interactive prompt or override env var.

## 12. LLM explanation layer
- in `orchestrator/explanation.py`: `ollama run llama3`.
- prompt read from `prompts/explanation.md`.

## 13. Outputs
Full output includes:
- validator
- alt_credit
- risk
- decision
- explanation
- trace

## 14. Conclusion
The project is now submission-ready and end-to-end runnable with `python run_full_system.py` in GitHub Codespaces, and includes required mechanisms for model training, pipeline, explanation, scenario tests, sub-agent evaluation, and tracing.
