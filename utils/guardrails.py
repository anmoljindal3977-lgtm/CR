import json
import re
from typing import Any, Dict, Tuple, Union

REQUIRED_FIELDS = {
    'SK_ID_CURR',
    'AMT_CREDIT',
    'AMT_INCOME_TOTAL',
    'AMT_ANNUITY',
    'DAYS_BIRTH',
    'DAYS_EMPLOYED',
    'EXT_SOURCE_1',
    'EXT_SOURCE_2',
    'EXT_SOURCE_3'
}

NUMERIC_FIELDS = {
    'SK_ID_CURR',
    'AMT_CREDIT',
    'AMT_INCOME_TOTAL',
    'AMT_ANNUITY',
    'DAYS_BIRTH',
    'DAYS_EMPLOYED',
    'EXT_SOURCE_1',
    'EXT_SOURCE_2',
    'EXT_SOURCE_3'
}

MAX_INPUT_LENGTH = 3000
MAX_FIELD_LENGTH = 512
HARMFUL_TERMS = {
    'kill', 'attack', 'bomb', 'terror', 'suicide', 'self-harm',
    'porn', 'drugs', 'illegal', 'hate', 'harass', 'exploit'
}

PROMPT_INJECTION_PATTERNS = [
    r'ignore (previous )?instructions',
    r'you are now',
    r'override (all )?rules',
    r'hack',
    r'system prompt',
    r'jailbreak',
    r'do anything'
]

PII_PATTERNS = [
    r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
    r'\b\d{3}[-\.\s]?\d{2}[-\.\s]?\d{4}\b',
    r'\b\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4}\b',
    r'\b(?:SSN|ID|passport|license)\b',
    r'\b\d{6,16}\b'
]

ALLOWED_FIELDS = REQUIRED_FIELDS


def _normalize_text(value: Any) -> str:
    if value is None:
        return ''
    if isinstance(value, str):
        return value.strip()
    return str(value)


def validate_raw_input(raw_input: Any) -> Tuple[bool, str]:
    """Validate the raw application input before any agent runs.

    This checks that the input is a JSON object with required credit fields,
    rejects off-domain field names, and prevents overly large or malformed inputs.
    """
    if raw_input is None:
        return False, 'Input is empty or null.'
    if not isinstance(raw_input, dict):
        return False, 'Input must be a JSON object/dict.'
    if not raw_input:
        return False, 'Input contains no fields.'

    if len(json.dumps(raw_input)) > MAX_INPUT_LENGTH:
        return False, 'Input is too large.'

    unknown_fields = set(raw_input.keys()) - ALLOWED_FIELDS
    if unknown_fields:
        return False, f'Unexpected field(s): {sorted(unknown_fields)}.'

    missing_fields = REQUIRED_FIELDS - set(raw_input.keys())
    if missing_fields:
        return False, f'Missing required field(s): {sorted(missing_fields)}.'

    for field, value in raw_input.items():
        if isinstance(value, str):
            if len(value) > MAX_FIELD_LENGTH:
                return False, f'Field {field} is too long.'
            if _contains_prompt_injection(value):
                return False, 'Prompt injection pattern detected.'
        if field in NUMERIC_FIELDS and not isinstance(value, (int, float)):
            return False, f'Field {field} must be numeric.'

    return True, 'Input structure validated.'


def _contains_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return True
    return False


def validate_input_schema(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Perform stricter type and domain validation on the normalized application dict."""
    if not isinstance(data, dict):
        return False, 'Data must be a dict.'

    for field in REQUIRED_FIELDS:
        if field not in data:
            return False, f'Missing required field: {field}.'
        if data[field] is None:
            return False, f'Field {field} must not be null.'

    # numeric field type enforcement
    for field in NUMERIC_FIELDS:
        value = data[field]
        if not isinstance(value, (int, float)):
            return False, f'Field {field} must be a numeric value.'

    return True, 'Input schema valid.'


def validate_output_schema(output: Any, schema_type: str = 'explanation') -> Tuple[bool, Any, str]:
    """Validate output shape and type for pipeline outputs and explanations."""
    if schema_type == 'explanation':
        if not isinstance(output, str):
            return False, output, 'Explanation output must be a string.'
        clean = output.strip()
        if not clean:
            return False, output, 'Explanation output is empty.'
        return True, clean, 'Explanation schema is valid.'

    if schema_type == 'pipeline_result':
        if not isinstance(output, dict):
            return False, output, 'Pipeline result must be a dictionary.'
        if 'decision' not in output or 'validator' not in output:
            return False, output, 'Pipeline result is missing required top-level fields.'
        return True, output, 'Pipeline result schema is valid.'

    return False, output, f'Unknown schema type: {schema_type}.'


def check_explanation_grounding(explanation: str, payload: Dict[str, Any]) -> Tuple[bool, str, str]:
    """Check that the explanation mentions the decision intent and does not contradict payload state."""
    if not isinstance(explanation, str):
        return False, explanation, 'Explanation must be text.'

    text = explanation.lower()
    decision = str(payload.get('decision', '')).upper()

    if decision == 'APPROVE' and 'approve' not in text and 'low risk' not in text:
        return False, explanation, 'Explanation does not mention approval grounding.'
    if decision == 'REJECT' and 'reject' not in text and 'high risk' not in text:
        return False, explanation, 'Explanation does not mention rejection grounding.'
    if decision == 'MANUAL_REVIEW' and 'manual' not in text and 'review' not in text:
        return False, explanation, 'Explanation does not mention manual review grounding.'
    if decision == 'INVALID' and 'invalid' not in text and 'rejected' not in text:
        return False, explanation, 'Explanation does not mention invalid input grounding.'

    return True, explanation, 'Explanation grounding validated.'


def redact_sensitive_data(output: Any) -> Tuple[bool, Any, str]:
    """Redacts obvious PII from text outputs so explanations cannot leak identifiers."""
    if not isinstance(output, str):
        return True, output, 'No redaction needed for non-text output.'

    text = output
    for pattern in PII_PATTERNS:
        text = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)

    return True, text, 'Sensitive data redacted.'


def filter_harmful_content(output: Any) -> Tuple[bool, Any, str]:
    """Detects and blocks harmful or off-topic content in text outputs."""
    if not isinstance(output, str):
        return True, output, 'No text to filter.'

    text = output.lower()
    found = [term for term in HARMFUL_TERMS if term in text]
    if found:
        return False, output, f'Harmful content detected: {found}.'
    return True, output, 'No harmful content detected.'
