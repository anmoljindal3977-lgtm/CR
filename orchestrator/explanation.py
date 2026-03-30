import subprocess

def generate_explanation(result: dict) -> str:
    p_default = result['risk']['p_default']
    alt_credit_score = result['alt_credit']['alt_credit_score']
    decision = result['decision']['decision']

    prompt = f"Explain this credit decision in simple terms:\n- default probability: {p_default}\n- alt credit score: {alt_credit_score}\n- decision: {decision}"

    # sending data to LLM
    result_proc = subprocess.run(['ollama', 'run', 'llama2', prompt], capture_output=True, text=True)

    # getting explanation
    explanation = result_proc.stdout.strip()

    return explanation