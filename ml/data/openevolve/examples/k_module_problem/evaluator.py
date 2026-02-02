"""
Evaluator for K-Module Pipeline Configuration Problem

This evaluator scores pipeline configurations based on how many modules
match the target configuration. The key property is that there's NO
gradient information - you only know the count of correct modules,
not WHICH ones are correct.

This creates a challenging landscape for iterative refinement but
allows evolutionary crossover to combine good "building blocks"
from different individuals.

Set RICH_FEEDBACK=1 to enable rich feedback mode, which tells you
exactly which modules are correct/incorrect. This demonstrates that
iterative refinement works well when feedback is attributable.
"""

import os
import sys
import time
import traceback
import importlib.util

# Rich feedback mode - when enabled, reveals which modules are correct
RICH_FEEDBACK = os.environ.get("RICH_FEEDBACK", "0") == "1"

# The correct solution (hidden from the optimizer)
# This represents the "optimal" pipeline configuration discovered through
# extensive testing/domain expertise
CORRECT_CONFIG = {
    'loader': 'csv_reader',
    'preprocess': 'normalize',
    'algorithm': 'quicksort',
    'formatter': 'json',
}

# Valid options for each module
VALID_OPTIONS = {
    'loader': ['csv_reader', 'json_reader', 'xml_reader', 'parquet_reader', 'sql_reader'],
    'preprocess': ['normalize', 'standardize', 'minmax', 'scale', 'none'],
    'algorithm': ['quicksort', 'mergesort', 'heapsort', 'bubblesort', 'insertion'],
    'formatter': ['json', 'xml', 'csv', 'yaml', 'protobuf'],
}

NUM_MODULES = len(CORRECT_CONFIG)


def evaluate(program_path: str) -> dict:
    """
    Evaluate a pipeline configuration program.

    Args:
        program_path: Path to the Python file containing configure_pipeline()

    Returns:
        dict with 'metrics' and optionally 'artifacts'
    """
    start_time = time.time()

    try:
        # Load and execute the program
        spec = importlib.util.spec_from_file_location("program", program_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["program"] = module
        spec.loader.exec_module(module)

        # Get the configuration
        if hasattr(module, 'run_pipeline'):
            config = module.run_pipeline()
        elif hasattr(module, 'configure_pipeline'):
            config = module.configure_pipeline()
        else:
            return _error_result("Program must define run_pipeline() or configure_pipeline()")

        # Validate the configuration
        validation_errors = validate_config(config)
        if validation_errors:
            return _validation_error_result(validation_errors)

        # Score the configuration
        correct_count, module_results = score_config(config)

        # Calculate metrics
        accuracy = correct_count / NUM_MODULES

        # The combined score rewards finding more correct modules
        # but gives NO information about which modules are correct
        combined_score = accuracy

        eval_time = time.time() - start_time

        # Build artifacts - provide feedback that helps evolution
        # but doesn't reveal which specific modules are wrong
        artifacts = build_artifacts(config, correct_count, module_results, eval_time)

        # Return metrics at top level for OpenEvolve compatibility
        return {
            "correct_modules": correct_count,
            "total_modules": NUM_MODULES,
            "accuracy": accuracy,
            "combined_score": combined_score,
            "eval_time": eval_time,
            "artifacts": artifacts,
        }

    except Exception as e:
        return _exception_result(e)


def validate_config(config: dict) -> list:
    """Validate that the configuration has valid values."""
    errors = []

    if not isinstance(config, dict):
        errors.append(f"Configuration must be a dict, got {type(config).__name__}")
        return errors

    # Check all required modules are present
    for module_name in CORRECT_CONFIG.keys():
        if module_name not in config:
            errors.append(f"Missing required module: '{module_name}'")
        elif config[module_name] not in VALID_OPTIONS[module_name]:
            errors.append(
                f"Invalid value for '{module_name}': '{config[module_name]}'. "
                f"Valid options: {VALID_OPTIONS[module_name]}"
            )

    return errors


def score_config(config: dict) -> tuple:
    """
    Score the configuration against the target.

    Returns:
        tuple: (correct_count, module_results dict)
    """
    correct_count = 0
    module_results = {}

    for module_name, correct_value in CORRECT_CONFIG.items():
        is_correct = config.get(module_name) == correct_value
        if is_correct:
            correct_count += 1
        module_results[module_name] = is_correct

    return correct_count, module_results


def build_artifacts(config: dict, correct_count: int, module_results: dict, eval_time: float) -> dict:
    """
    Build artifacts that provide useful feedback.

    In normal mode: Only reveals how many modules are correct, not which ones.
    In rich feedback mode (RICH_FEEDBACK=1): Reveals exactly which modules are correct/incorrect.
    """
    artifacts = {}

    # Configuration summary
    artifacts["configuration"] = str(config)

    # Rich feedback mode - reveals which modules are correct/incorrect
    if RICH_FEEDBACK:
        correct_modules = [m for m, is_correct in module_results.items() if is_correct]
        incorrect_modules = [m for m, is_correct in module_results.items() if not is_correct]

        artifacts["module_feedback"] = {
            "correct": correct_modules,
            "incorrect": incorrect_modules,
        }

        if incorrect_modules:
            hints = []
            for module in incorrect_modules:
                hints.append(f"'{module}' is WRONG - try a different option from {VALID_OPTIONS[module]}")
            artifacts["actionable_hints"] = hints
        else:
            artifacts["actionable_hints"] = ["All modules are correct!"]

    # Score feedback - tells you how many are correct, but not which ones
    if correct_count == NUM_MODULES:
        artifacts["status"] = "PERFECT! All modules correctly configured!"
        artifacts["suggestion"] = "Optimal configuration found."
    elif correct_count >= NUM_MODULES - 1:
        artifacts["status"] = f"Very close! {correct_count}/{NUM_MODULES} modules correct."
        artifacts["suggestion"] = "One module may need adjustment. Try variations."
    elif correct_count >= NUM_MODULES // 2:
        artifacts["status"] = f"Good progress: {correct_count}/{NUM_MODULES} modules correct."
        artifacts["suggestion"] = "Some modules are correct. Explore different combinations."
    else:
        artifacts["status"] = f"Needs improvement: {correct_count}/{NUM_MODULES} modules correct."
        artifacts["suggestion"] = "Try different options for each module. Consider the problem domain."

    # Hints about the problem structure (not the solution)
    artifacts["problem_hints"] = (
        "Each module choice is independent. "
        "The optimal loader processes the most common data format. "
        "The optimal preprocessing creates unit variance. "
        "The optimal algorithm has O(n log n) average case. "
        "The optimal formatter is widely used for APIs."
    )

    artifacts["search_space"] = f"{5**NUM_MODULES} possible combinations"
    artifacts["eval_time"] = f"{eval_time:.3f}s"

    return artifacts


def _error_result(message: str) -> dict:
    """Return an error result."""
    return {
        "metrics": {
            "correct_modules": 0,
            "total_modules": NUM_MODULES,
            "accuracy": 0.0,
            "combined_score": 0.0,
        },
        "artifacts": {
            "error": message,
            "status": "ERROR",
        },
    }


def _validation_error_result(errors: list) -> dict:
    """Return a validation error result."""
    return {
        "metrics": {
            "correct_modules": 0,
            "total_modules": NUM_MODULES,
            "accuracy": 0.0,
            "combined_score": 0.0,
        },
        "artifacts": {
            "validation_errors": "\n".join(errors),
            "status": "VALIDATION_ERROR",
            "suggestion": "Fix the configuration to use valid module options.",
        },
    }


def _exception_result(e: Exception) -> dict:
    """Return an exception result."""
    return {
        "metrics": {
            "correct_modules": 0,
            "total_modules": NUM_MODULES,
            "accuracy": 0.0,
            "combined_score": 0.0,
        },
        "artifacts": {
            "exception": str(e),
            "traceback": traceback.format_exc(),
            "status": "EXCEPTION",
        },
    }


# For standalone testing
if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = evaluate(sys.argv[1])
        print(f"Metrics: {result['metrics']}")
        print(f"Artifacts: {result.get('artifacts', {})}")
    else:
        # Test with the initial program
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        initial_program = os.path.join(script_dir, "initial_program.py")
        result = evaluate(initial_program)
        print(f"Metrics: {result['metrics']}")
        print(f"Artifacts: {result.get('artifacts', {})}")
