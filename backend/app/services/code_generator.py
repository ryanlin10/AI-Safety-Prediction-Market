"""
AI-powered code generation for rigorous hypothesis testing
Uses OpenAI GPT-4 to generate Python test code
"""
from openai import OpenAI
import os

def generate_test_code(investigation_data: dict) -> dict:
    """
    Generate Python code to test a research hypothesis using AI
    
    Args:
        investigation_data: Dict containing:
            - hypothesis: The research claim to test
            - formalized_claim: Formalized version of the claim
            - context: Additional context about the research
            
    Returns:
        Dict with:
            - main_py: Generated Python code for main.py
            - additional_files: Dict of any additional files needed
            - explanation: Explanation of the approach
    """
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        raise Exception("OpenAI API key not configured")
    
    client = OpenAI(api_key=api_key)
    
    hypothesis = investigation_data.get('hypothesis', '')
    formalized_claim = investigation_data.get('formalized_claim', '')
    context = investigation_data.get('context', '')
    
    # Construct prompt for code generation
    prompt = f"""You are an expert research scientist and Python developer. Generate rigorous, production-quality Python code to test the following research hypothesis.

HYPOTHESIS: {hypothesis}

FORMALIZED CLAIM: {formalized_claim}

CONTEXT: {context}

Generate a complete Python script that:
1. Implements a rigorous test of this hypothesis
2. Uses appropriate ML/statistical methods (numpy, pandas, scipy, sklearn, torch, etc.)
3. Generates synthetic or example data if needed (no external data fetching)
4. Performs statistical analysis
5. Outputs clear results with confidence metrics
6. Includes proper error handling
7. Has clear comments explaining the methodology

REQUIREMENTS:
- Use only allowed libraries: numpy, pandas, scipy, sklearn, torch, matplotlib, seaborn
- NO network requests, file I/O, or system calls
- Generate synthetic data within the script
- Output results using print() statements
- Include statistical significance testing where appropriate
- Return a conclusion: "LIKELY TRUE", "LIKELY FALSE", or "INCONCLUSIVE"

Format your response as a complete, executable Python script. Start directly with the code, no markdown formatting."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4o-mini for code generation
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert research scientist and Python developer specializing in rigorous hypothesis testing and statistical analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        generated_code = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if generated_code.startswith('```python'):
            generated_code = generated_code[len('```python'):].strip()
        if generated_code.startswith('```'):
            generated_code = generated_code[3:].strip()
        if generated_code.endswith('```'):
            generated_code = generated_code[:-3].strip()
        
        # Generate explanation
        explanation_prompt = f"""Briefly explain the testing approach used in this code in 2-3 sentences:

{generated_code[:500]}..."""

        explanation_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": explanation_prompt
                }
            ],
            temperature=0.5,
            max_tokens=200
        )
        
        explanation = explanation_response.choices[0].message.content.strip()
        
        return {
            'main_py': generated_code,
            'additional_files': {},
            'explanation': explanation,
            'model_used': 'gpt-4o-mini'
        }
        
    except Exception as e:
        # Fallback to template if AI generation fails
        fallback_code = f"""# AI Code Generation Failed: {str(e)}
# Fallback template for testing: {hypothesis}

import numpy as np
import pandas as pd
from scipy import stats

def test_hypothesis():
    \"\"\"
    Test hypothesis: {hypothesis}
    
    Formalized: {formalized_claim}
    \"\"\"
    print("=" * 60)
    print("RIGOROUS HYPOTHESIS TEST")
    print("=" * 60)
    print(f"Hypothesis: {hypothesis}")
    print()
    
    # TODO: Implement your test here
    # Generate synthetic data
    np.random.seed(42)
    sample_size = 100
    
    # Placeholder analysis
    print("Generating synthetic data...")
    data = np.random.normal(0, 1, sample_size)
    
    print(f"Sample size: {{sample_size}}")
    print(f"Mean: {{np.mean(data):.4f}}")
    print(f"Std: {{np.std(data):.4f}}")
    print()
    
    # Perform statistical test
    t_stat, p_value = stats.ttest_1samp(data, 0)
    print(f"T-statistic: {{t_stat:.4f}}")
    print(f"P-value: {{p_value:.4f}}")
    print()
    
    # Conclusion
    alpha = 0.05
    if p_value < alpha:
        print("Result: STATISTICALLY SIGNIFICANT")
        print("Conclusion: INCONCLUSIVE (needs real data)")
    else:
        print("Result: NOT STATISTICALLY SIGNIFICANT")
        print("Conclusion: INCONCLUSIVE (needs real data)")
    
    print("=" * 60)

if __name__ == "__main__":
    test_hypothesis()
"""
        
        return {
            'main_py': fallback_code,
            'additional_files': {},
            'explanation': f"AI generation failed: {str(e)}. Using fallback template.",
            'model_used': 'fallback'
        }

