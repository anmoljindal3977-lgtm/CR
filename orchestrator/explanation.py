"""
This file generates explanations for decisions using LLM.
"""

import subprocess
import json
from utils.guardrails import (
    validate_output_schema,
    check_explanation_grounding,
    redact_sensitive_data,
    filter_harmful_content
)


def _compose_prompt(payload: dict) -> str:
    base = """
# Role
You are a credit risk assistant.

# Task
Explain the system outcome in simple, clear terms.

# Input Format
JSON with fields:
- status (VALID / INVALID)
- decision (APPROVE / REJECT / MANUAL_REVIEW / INVALID)
- p_default (number or null)
- alt_credit_score (number or null)
- reason (string)

# Examples (Few-shot)
Example 1:
Input:
{"status": "VALID", "decision": "APPROVE", "p_default": 0.03, "alt_credit_score": 0.9, "reason": "Low risk"}
Output:
"Low risk, likely to repay."

Example 2:
Input:
{"status": "VALID", "decision": "REJECT", "p_default": 0.25, "alt_credit_score": 0.2, "reason": "High default probability"}
Output:
"High risk of default, not recommended."

Example 3:
Input:
{"status": "INVALID", "decision": "INVALID", "p_default": null, "alt_credit_score": null, "reason": "INJECTION_DETECTED"}
Output:
"Input contains malicious content and is rejected for safety."

# Instructions
- Explain the system outcome clearly.
- If decision is APPROVE -> explain low risk.
- If decision is REJECT -> explain high risk or failure reason.
- If decision is MANUAL_REVIEW -> explain uncertainty and next steps.
- If decision is INVALID -> explain input issue.
- If INJECTION detected -> explain unsafe input detected.
- Do NOT return empty response.
- Do NOT say \"N/A\".
- Always provide meaningful explanation.

Input:
"""
    input_json = json.dumps(payload, ensure_ascii=False)
    return base + input_json + "\n\nOutput:" 


def _fallback_explanation(payload: dict) -> str:
    decision = payload.get('decision', 'INVALID')
    if decision == 'APPROVE':
        return "Approve: credit is low risk based on score model and alternative credit check."
    if decision == 'REJECT':
        return "Reject: high risk or validation issue detected."
    if decision == 'MANUAL_REVIEW':
        return "Manual review: edge case requires human in-the-loop decision."
    if decision == 'INVALID':
        reason = payload.get('reason', 'Validation failed')
        return f"Invalid input: {reason}."
    return "Could not generate explanation, please revisit the input."


def generate_explanation(result: dict) -> str:
    if "decision" not in result:
        # Should not happen with pipeline but is safe path.
        payload = {
            "status": "INVALID",
            "decision": "INVALID",
            "p_default": None,
            "alt_credit_score": None,
            "reason": result.get("validator", {}).get("reason", "Unknown failure")
        }
    else:
        decision_data = result.get("decision", {})
        validator_data = result.get("validator", {})

        status = "VALID" if validator_data.get("status") == "PASS" else "INVALID"
        decision_key = decision_data.get("decision", "INVALID")

        p_default = None
        alt_credit_score = None
        if result.get("risk"):
            p_default = result["risk"].get("p_default")
        if result.get("alt_credit"):
            alt_credit_score = result["alt_credit"].get("alt_credit_score")

        payload = {
            "status": status,
            "decision": decision_key,
            "p_default": p_default,
            "alt_credit_score": alt_credit_score,
            "reason": decision_data.get("reason") or validator_data.get("reason") or "No reason provided"
        }

    prompt_text = _compose_prompt(payload)

    try:
        llm_proc = subprocess.run(
            ['ollama', 'run', 'llama3'],
            input=prompt_text,
            capture_output=True,
            text=True,
            timeout=20
        )

        raw_out = llm_proc.stdout.strip() if llm_proc.stdout else ""
        if llm_proc.returncode != 0 or not raw_out:
            raise RuntimeError(llm_proc.stderr.strip() if llm_proc.stderr else "ollama invocation failed")

        explanation = raw_out
        if explanation.upper() == "N/A" or explanation == "":
            raise RuntimeError("Invalid explanation from LLM")

        print("Guardrail: Applying validate_output_schema...")
        schema_valid, explanation, schema_reason = validate_output_schema(explanation, schema_type='explanation')
        if not schema_valid:
            raise RuntimeError(schema_reason)
        print("Schema validation passed")

        print("Guardrail: Applying check_explanation_grounding...")
        grounded, _, grounding_reason = check_explanation_grounding(explanation, payload)
        if not grounded:
            raise RuntimeError(grounding_reason)
        print("Explanation grounding check passed")

        print("Guardrail: Applying redact_sensitive_data...")
        redacted_ok, explanation, _ = redact_sensitive_data(explanation)
        if not redacted_ok:
            raise RuntimeError("PII redaction failed")
        print(" PII redaction completed")

        print("Guardrail: Applying filter_harmful_content...")
        filtered, explanation, filter_reason = filter_harmful_content(explanation)
        if not filtered:
            raise RuntimeError(filter_reason)
        print(" Harmful content filtering passed")

        return explanation

    except Exception:
        return _fallback_explanation(payload)

