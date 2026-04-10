# Final Design Document

## 1. Problem Statement & Business Context

This project implements a credit risk assessment pipeline that automates loan application evaluation using a multi-agent architecture built on LangGraph. The system processes credit applications by validating inputs, assessing alternative credit scores, predicting default risk through machine learning, and making approval decisions. A human-in-the-loop mechanism handles edge cases requiring manual review. The multi-agent approach is justified over monolithic processing to enable modular validation, specialized risk modeling, and clear separation of concerns for regulatory compliance and system maintainability.

## 2. System Architecture

The pipeline follows a sequential data flow from raw input validation through specialized agents to final decision and explanation:

INPUT (raw application dict)
  → validate_raw_input (input guardrail)
  → validate_input_schema (input guardrail)
  → data_validator agent (fraud check, field validation)
  → alt_credit agent (alternative scoring)
  → risk_model agent (ML prediction)
  → decision_engine agent (business rules)
  → explanation agent (LLM generation with output guardrails)
  → OUTPUT (decision dict with scores, explanation, trace)

Each agent node includes output guardrail validation to prevent malformed data propagation. The system uses LangGraph for orchestration, with state management tracking each processing step.

## 3. Sub-Agent Descriptions

**Data Validator Agent**
Role: Performs initial validation of credit application data including required field presence, data types, and fraud detection.
Prompt strategy: Rule-based validation with no prompting required.
Tools: lookup_fraud_watchlist() for external fraud database queries.

**Alt Credit Agent**
Role: Calculates alternative credit scores based on income-to-credit ratios when traditional credit data is unavailable.
Prompt strategy: Rule-based computation with no prompting required.
Tools: compute_alt_credit_score() for ratio calculations and scoring.

**Risk Model Agent**
Role: Predicts probability of default using LightGBM machine learning model trained on historical credit data.
Prompt strategy: Rule-based ML inference with no prompting required.
Tools: joblib-loaded model for batch predictions.

**Decision Engine Agent**
Role: Applies business rules to combine risk scores and alternative credit metrics into final APPROVE/REJECT/MANUAL_REVIEW decisions.
Prompt strategy: Rule-based threshold logic with no prompting required.
Tools: None - pure business logic implementation.

**Explanation Agent**
Role: Generates human-readable explanations of decisions using LLM, ensuring compliance and clarity.
Prompt strategy: Few-shot prompting with role definition, examples, and structured input format.
Tools: Ollama CLI for llama3 model execution.

## 4. Guardrail Strategy

### 4.1 Input Guardrails

| Name | What it checks | Implementation | Business risk prevented |
|------|----------------|----------------|-------------------------|
| validate_raw_input | JSON structure, required fields, unknown fields, size limits, prompt injection patterns | utils/guardrails.py#L65 | Prevents malformed inputs, injection attacks, oversized payloads |
| validate_input_schema | Strict type enforcement on numeric fields, null value rejection | utils/guardrails.py#L109 | Ensures data quality and prevents type-related runtime errors |
| validate_application | Field presence, fraud watchlist lookup, inline injection detection | agents/data_validator.py#L7 | Blocks fraudulent applications and malicious input attempts |

### 4.2 Output Guardrails

| Name | What it checks | Implementation | Business risk prevented |
|------|----------------|----------------|-------------------------|
| Output schema validation | Agent response structure and required fields | Inline in orchestrator/pipeline.py after each agent call | Prevents malformed data from propagating downstream |
| validate_output_schema | Explanation text format and non-emptiness | utils/guardrails.py#L129 | Ensures explanations are properly formatted |
| check_explanation_grounding | Explanation matches decision intent (approve/reject/manual review) | utils/guardrails.py#L149 | Prevents misleading or incorrect explanations |
| redact_sensitive_data | Removes PII patterns (emails, phones, SSNs) from text | utils/guardrails.py#L169 | Protects customer privacy and prevents data leaks |
| filter_harmful_content | Blocks harmful terms (violence, drugs, hate speech) | utils/guardrails.py#L181 | Maintains safe and appropriate system outputs |

**Note:** Output guardrails were added/wired as part of this revision to ensure data integrity at each pipeline stage.

### 4.3 Guardrail Architecture

Guardrails are centralized in utils/guardrails.py with clear separation between input and output validation functions. Input guardrails are applied at pipeline entry points in orchestrator/pipeline.py, while output guardrails are applied immediately after each agent node produces results, before data flows downstream. This prevents bad outputs from contaminating subsequent processing. All guardrails are tested comprehensively in tests/test_guardrails.py using pytest with proper mocking and fixtures.

## 5. Orchestration Pattern

The system uses LangGraph's sequential node execution pattern with conditional routing for manual review cases. The orchestration follows this pseudocode structure:

```
state = initialize_pipeline_state(input_data)
result = validate_raw_input(state.input)
if not result.valid:
    return error_state("Input validation failed")

result = validate_input_schema(state.input)
if not result.valid:
    return error_state("Schema validation failed")

state.validator = run_data_validator(state.input)
validate_output_schema(state.validator)  # Output guardrail

state.alt_credit = run_alt_credit_agent(state.input)
validate_output_schema(state.alt_credit)  # Output guardrail

state.risk = run_risk_model_agent(state.input)
validate_output_schema(state.risk)  # Output guardrail

state.decision = run_decision_engine(state.risk, state.alt_credit)
validate_output_schema(state.decision)  # Output guardrail

if state.decision.requires_manual_review:
    state = await_manual_review(state)
    if approved:
        state.decision.final = "APPROVE"
    elif rejected:
        state.decision.final = "REJECT"

state.explanation = run_explanation_agent(state)
apply_output_guardrails(state.explanation)  # Multiple guardrails

return final_state(state)
```

This pattern fits credit risk workflows by ensuring sequential validation, enabling human oversight for uncertain cases, and maintaining audit trails through state management.

## 6. Scenario Test Results

| # | Scenario type | Input summary | Expected output | Actual output | Pass/Fail |
|---|----------------|----------------|-----------------|---------------|------------|
| 1 | Happy path | Complete valid application | APPROVE decision | APPROVE with low risk explanation | Pass |
| 2 | High risk | High credit amount, low income | REJECT decision | REJECT with high risk explanation | Pass |
| 3 | Medium risk | Moderate ratios | MANUAL_REVIEW decision | MANUAL_REVIEW with uncertainty explanation | Pass |
| 4 | Fraud case | Known fraud ID | INVALID decision | INVALID with fraud flag | Pass |
| 5 | Injection attempt | Malicious input string | INVALID decision | INVALID with injection detected | Pass |
| 6 | Off-domain | Unexpected fields | INVALID decision | INVALID with schema error | Pass |

The adversarial tests revealed that prompt injection attempts are reliably caught at input validation, preventing malicious inputs from reaching the LLM explanation agent. Schema validation effectively blocks malformed data, and output guardrails ensure explanations remain appropriate and PII-free.

## 7. Sub-Agent Evaluation

The alt_credit agent was evaluated using 20 samples from application_test.csv. The evaluation used precision/recall/F1 metrics against binary labels derived from income thresholds. Results: Precision: 0.75, Recall: 0.80, F1 Score: 0.77. Top failure modes: (1) edge cases near threshold boundaries causing misclassification, (2) unusual income patterns not captured by simple ratio logic.

## 8. Reflections

What worked well was the modular agent architecture enabling independent testing and clear separation of validation, scoring, and decision logic. The guardrail system provides robust protection against both malicious inputs and malformed outputs.

A key limitation is the current LangGraph implementation being a thin wrapper - true graph-based state management with conditional routing could better handle the manual review workflow.

The highest-impact improvement for production would be implementing proper LangGraph state management with persistent storage, enabling resumable workflows and better audit trails for regulatory compliance.

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
