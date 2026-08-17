# Known Issues

Found during a review/run pass on 2026-08-17. Not fixed yet — logged here for later.

## `tests/test_guardrails.py` — 6 failing tests (22 pass)

1. **`test_pipeline_accepts_valid_input_full_flow`** (line 255) — calls `run_langgraph_pipeline(...)` (correct spelling), but the function imported at the top of the file (and defined in `orchestrator/langgraoh_pipline.py`) is spelled `run_langgraoh_pipline`. Raises `NameError`.

2. **`test_validate_raw_input_oversized_input`** — asserts `"long"` appears in the rejection message. The oversized payload also exceeds `MAX_INPUT_LENGTH` (checked before the per-field `MAX_FIELD_LENGTH` check in `utils/guardrails.py:validate_raw_input`), so the actual message is `"Input is too large."`, not a per-field "too long" message.

3. **`test_filter_harmful_content_clean`** — asserts `"detected"` is absent from the message on the clean-content pass path, but `filter_harmful_content`'s pass message is itself `"No harmful content detected."` (contains "detected").

4. **`test_pipeline_rejects_malformed_validator_output`** — asserts `"validation failed"` in the reason, but the actual fallback reason from `_validate_agent_output` is `"Validator output schema invalid"`.

5. **`test_pipeline_rejects_malformed_alt_credit_output`** — same wording mismatch pattern as #4.

6. **`test_pipeline_rejects_malformed_risk_output`** — asserts the pipeline decision becomes `INVALID` when `predict_risk` returns malformed output. In `orchestrator/langgraoh_pipline.py`, only the **validator** step short-circuits to an `INVALID` decision; `alt_credit`/`risk` steps instead fall back to safe defaults (`p_default=1.0` etc.) and the pipeline continues normally to `decision_engine`, which returns `REJECT` (high `p_default`) rather than `INVALID`.

## Operational note (not a bug, but worth fixing before CI use)

`run_scenarios.py` calls `run_langgraoh_pipline(data, interactive=True)` without a `manual_override`. Any scenario landing on `MANUAL_REVIEW` will block on `input()` if stdin isn't available (e.g. in CI). Workaround used during this run: `export MANUAL_REVIEW_OVERRIDE=n` before invoking the script.
