"""
This file generates explanations for decisions using LLM.
"""

import subprocess

def generate_explanation(result: dict) -> str:
    """
    Takes pipeline result and gets human explanation from LLM.
    """
    p_default = result['risk']['p_default']
    alt_credit_score = result['alt_credit']['alt_credit_score']
    decision = result['decision']['decision']

    # load prompt from file
    with open('prompts/explanation.md', 'r') as f:
        prompt_base = f.read()

    input_data = f"\n\nInput:\np_default: {p_default}\nalt_credit_score: {alt_credit_score}\ndecision: {decision}"

    full_prompt = prompt_base + input_data

    # sending data to LLM
    result_proc = subprocess.run(['ollama', 'run', 'llama2', full_prompt], capture_output=True, text=True)

    # getting explanation
    explanation = result_proc.stdout.strip()

    return explanation