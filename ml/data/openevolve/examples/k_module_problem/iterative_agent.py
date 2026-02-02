#!/usr/bin/env python3
"""
Iterative Refinement Agent for K-Module Problem

This implements a simple iterative refinement approach that:
1. Reads the current program
2. Asks the LLM to improve it based on evaluation feedback
3. Evaluates the new program
4. Repeats until solution found or max iterations reached

Uses OpenRouter API (OpenAI-compatible) with the same model as OpenEvolve
for fair comparison.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import yaml
from openai import OpenAI

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from evaluator import evaluate, VALID_OPTIONS, NUM_MODULES


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def extract_code_block(response: str) -> str:
    """Extract Python code from LLM response."""
    # Try to find code block with ```python
    pattern = r"```python\s*(.*?)\s*```"
    matches = re.findall(pattern, response, re.DOTALL)
    if matches:
        return matches[-1].strip()  # Return last code block

    # Try to find code block with just ```
    pattern = r"```\s*(.*?)\s*```"
    matches = re.findall(pattern, response, re.DOTALL)
    if matches:
        return matches[-1].strip()

    # Return the whole response if no code block found
    return response.strip()


def read_program(program_path: str) -> str:
    """Read program from file."""
    with open(program_path) as f:
        return f.read()


def write_program(program_path: str, code: str) -> None:
    """Write program to file."""
    with open(program_path, "w") as f:
        f.write(code)


def format_rich_feedback(artifacts: dict) -> str:
    """Format rich feedback if available (RICH_FEEDBACK=1)."""
    if "module_feedback" not in artifacts:
        return ""

    feedback = artifacts["module_feedback"]
    hints = artifacts.get("actionable_hints", [])

    result = "\n## DETAILED MODULE FEEDBACK (Rich Feedback Mode)\n"
    result += f"- CORRECT modules: {feedback.get('correct', [])}\n"
    result += f"- INCORRECT modules: {feedback.get('incorrect', [])}\n"

    if hints:
        result += "\n### Actionable Hints:\n"
        for hint in hints:
            result += f"- {hint}\n"

    return result


def create_improvement_prompt(
    current_code: str,
    metrics: dict,
    artifacts: dict,
    iteration: int,
    history: list
) -> str:
    """Create prompt asking LLM to improve the program."""

    history_str = ""
    if history:
        history_str = "\n## Previous Attempts\n"
        for h in history[-5:]:  # Last 5 attempts
            history_str += f"\nIteration {h['iteration']}:\n"
            history_str += f"- Score: {h['metrics'].get('correct_modules', 0)}/{NUM_MODULES} modules correct\n"
            history_str += f"- Configuration tried: {h['artifacts'].get('configuration', 'N/A')}\n"

    prompt = f"""You are optimizing a data processing pipeline configuration.

## Problem
Find the correct configuration for a 4-component pipeline. Each module has 5 options:
- loader: {VALID_OPTIONS['loader']}
- preprocess: {VALID_OPTIONS['preprocess']}
- algorithm: {VALID_OPTIONS['algorithm']}
- formatter: {VALID_OPTIONS['formatter']}

## Hints
- The optimal loader processes the most common data format
- The optimal preprocessing creates unit variance
- The optimal algorithm has O(n log n) average case
- The optimal formatter is widely used for APIs

## Current Iteration: {iteration}

## Current Code
```python
{current_code}
```

## Last Evaluation Result
- Correct modules: {metrics.get('correct_modules', 0)}/{NUM_MODULES}
- Score: {metrics.get('combined_score', 0):.2%}
- Status: {artifacts.get('status', 'N/A')}
- Suggestion: {artifacts.get('suggestion', 'N/A')}
{format_rich_feedback(artifacts)}
{history_str}

## Your Task
Modify the configure_pipeline() function to try a DIFFERENT configuration.
Think about what each hint suggests and try to find the optimal combination.

IMPORTANT:
- Return ONLY the complete Python code with EVOLVE-BLOCK markers
- Try a different combination than previous attempts
- The code must be valid Python that can be executed

Return the improved code:
"""
    return prompt


SYSTEM_PROMPT = """You are an expert programmer optimizing code through iterative refinement.
Your task is to improve Python programs based on evaluation feedback.

When given a program and its evaluation results:
1. Analyze what the current configuration is doing
2. Think about what the hints suggest
3. Propose a new configuration that might score better
4. Return the complete modified code

Always return valid Python code within ```python``` code blocks.
Only modify the configuration values, keep the code structure intact."""


def run_iterative_refinement(
    initial_program: str,
    evaluator_path: str,
    config: dict,
    max_iterations: int = 100,
    output_dir: str = "iterative_output"
) -> dict:
    """
    Run iterative refinement loop.

    Returns:
        dict with results including iterations, scores, solution_found_at
    """
    # Setup output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Setup OpenAI client with OpenRouter
    llm_config = config.get("llm", {})
    api_base = llm_config.get("api_base", "https://openrouter.ai/api/v1")
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY or OPENAI_API_KEY must be set")

    client = OpenAI(base_url=api_base, api_key=api_key)

    # Get model from config
    models = llm_config.get("models", [])
    model_name = models[0].get("name", "google/gemini-2.5-flash-lite") if models else "google/gemini-2.5-flash-lite"
    temperature = llm_config.get("temperature", 0.7)
    max_tokens = llm_config.get("max_tokens", 4096)

    print(f"Using model: {model_name}")
    print(f"API base: {api_base}")
    print(f"Max iterations: {max_iterations}")
    print()

    # Initialize
    current_program_path = output_path / "current_program.py"

    # Copy initial program
    initial_code = read_program(initial_program)
    write_program(str(current_program_path), initial_code)

    results = {
        "iterations": [],
        "scores": [],
        "best_scores": [],
        "solution_found_at": None,
        "history": [],
        "model": model_name,
        "api_base": api_base,
    }

    best_score = 0
    history = []

    for iteration in range(max_iterations):
        print(f"\n{'='*50}")
        print(f"Iteration {iteration + 1}/{max_iterations}")
        print('='*50)

        # Read current program
        current_code = read_program(str(current_program_path))

        # Evaluate current program
        eval_result = evaluate(str(current_program_path))
        # Handle both flat (success) and nested (error) return formats
        if "metrics" in eval_result:
            metrics = eval_result["metrics"]
        else:
            metrics = {k: v for k, v in eval_result.items() if k != "artifacts"}
        artifacts = eval_result.get("artifacts", {})

        score = metrics.get("combined_score", 0)
        correct = metrics.get("correct_modules", 0)

        print(f"Score: {correct}/{NUM_MODULES} modules correct ({score:.2%})")
        print(f"Config: {artifacts.get('configuration', 'N/A')}")

        # Record results
        results["iterations"].append(iteration)
        results["scores"].append(score)
        best_score = max(best_score, score)
        results["best_scores"].append(best_score)

        history.append({
            "iteration": iteration,
            "metrics": metrics,
            "artifacts": artifacts,
        })

        # Check if solution found
        if score >= 1.0:
            print(f"\n*** SOLUTION FOUND at iteration {iteration + 1}! ***")
            results["solution_found_at"] = iteration
            break

        # Generate improvement
        prompt = create_improvement_prompt(
            current_code, metrics, artifacts, iteration + 1, history
        )

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            response_text = response.choices[0].message.content
            new_code = extract_code_block(response_text)

            # Validate the new code has the required structure
            if "configure_pipeline" in new_code and "EVOLVE-BLOCK" in new_code:
                write_program(str(current_program_path), new_code)
                print("Generated new configuration")
            else:
                print("Warning: Invalid code generated, keeping current")

        except Exception as e:
            print(f"Error generating improvement: {e}")
            continue

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    # Save final results
    results["history"] = history
    results["final_best_score"] = best_score
    results["total_iterations"] = len(results["iterations"])

    with open(output_path / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*50}")
    print("ITERATIVE REFINEMENT COMPLETE")
    print('='*50)
    print(f"Total iterations: {len(results['iterations'])}")
    print(f"Best score: {best_score:.2%}")
    if results["solution_found_at"] is not None:
        print(f"Solution found at iteration: {results['solution_found_at'] + 1}")
    else:
        print("Solution NOT found")
    print(f"Results saved to: {output_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Iterative refinement agent for K-Module problem")
    parser.add_argument("--initial-program", default="initial_program.py", help="Initial program path")
    parser.add_argument("--evaluator", default="evaluator.py", help="Evaluator path")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument("--iterations", type=int, default=100, help="Max iterations")
    parser.add_argument("--output", default="iterative_output", help="Output directory")
    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    # Run iterative refinement
    results = run_iterative_refinement(
        initial_program=args.initial_program,
        evaluator_path=args.evaluator,
        config=config,
        max_iterations=args.iterations,
        output_dir=args.output,
    )

    return 0 if results["solution_found_at"] is not None else 1


if __name__ == "__main__":
    sys.exit(main())
