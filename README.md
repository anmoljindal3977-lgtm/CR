# Credit Risk Multi-Agent Pipeline

## Project Overview
- Project title: Credit Risk Multi-Agent Pipeline
- Domain: credit risk / finance
- Short description: A credit risk decision system built with modular agents. It validates applications, predicts risk, decides approve/reject/manual review, and adds LLM explanations.
- End-to-end: input data → validator → alt credit score → risk model → decision engine → LLM explanation → output with trace.

## Problem Statement
- Business problem: decide loan requests quickly and consistently.
- Input to output:
  - data in (SK_ID_CURR, income, credit, demographics)
  - output out (decision, reason, explanation, trace)
- Automation is useful to avoid manual delays and human inconsistency.

## System Architecture
- Pipeline:
  - input → validator → alt credit → risk model → decision → LLM explanation → trace
- Modular agents:
  - `agents/data_validator.py`
  - `agents/alt_credit.py`
  - `agents/risk_model.py`
  - `agents/decision_engine.py`
  - `orchestrator/explanation.py`
- Orchestration via `orchestrator/pipeline.py` and LangGraph wrapper `orchestrator/langgraph_pipeline.py`.

## Deliverables
1. **GitHub Repository**
   - modular structure.
   - agents, tools, pipeline.

2. **Runner Script / Notebook**
   - `run_full_system.py` runs full flow.

3. **Scenario Testing File**
   - `run_scenarios.py` outputs `deliverables/` results.

4. **Sub-Agent Evaluation Package**
   - dataset from `data/application_test.csv` (15-20 samples)
   - `evaluation/evaluate_alt_credit.py`, metrics output.

5. **Design Document**
   - `docs/final_design_document.md`.

6. **Observability / Trace Evidence**
   - trace logs in results.

## Setup Instructions
```bash
git clone <repo-url>
cd CR
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## LLM Setup (Ollama)
Linux / Codespaces:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull llama3
```
- LLM used for explanation layer only.

## How to Run the Project
1. `python train_model.py`
2. `python main.py`
3. `python run_scenarios.py`
4. `python run_full_system.py`

## Outputs
- Model: `models/risk_model.pkl`
- scenario outputs: `deliverables/scenario_test_results.json`, `deliverables/scenario_test_results_table.md`
- full run output: `deliverables/run_full_system_output.json`
- contains decision, explanation, trace.

## Scenario Testing
- 5+ scenarios: normal, edge, adversarial, invalid, manual-review.
- each includes explanation.

## Sub-Agent Evaluation
- uses 15-20 labelled sample rows.
- script `evaluation/evaluate_alt_credit.py`.
- metric F1 (plus precision/recall).

## Key Features
- multi-agent design
- input guardrails
- LLM explanation layer
- observability trace
- human-in-loop manual review

## Notes
- dataset source: public dataset (Kaggle style)
- reproducible and modular implementation

