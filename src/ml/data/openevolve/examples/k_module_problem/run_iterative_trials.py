#!/usr/bin/env python3
"""Run multiple trials of iterative refinement to get statistics."""

import json
import os
import shutil
import sys
from pathlib import Path

# Run from the example directory
os.chdir(Path(__file__).parent)

from iterative_agent import run_iterative_refinement, load_config


def run_trials(num_trials: int = 10, max_iterations: int = 100):
    """Run multiple trials and collect statistics."""
    config = load_config("config.yaml")

    results = []
    solutions_found = []

    for trial in range(num_trials):
        print(f"\n{'#'*60}")
        print(f"# TRIAL {trial + 1}/{num_trials}")
        print('#'*60)

        # Clean output directory for each trial
        output_dir = f"iterative_output_trial_{trial}"
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        # Run trial
        result = run_iterative_refinement(
            initial_program="initial_program.py",
            evaluator_path="evaluator.py",
            config=config,
            max_iterations=max_iterations,
            output_dir=output_dir,
        )

        results.append({
            "trial": trial,
            "solution_found_at": result["solution_found_at"],
            "final_best_score": result["final_best_score"],
            "total_iterations": result["total_iterations"],
        })

        if result["solution_found_at"] is not None:
            solutions_found.append(result["solution_found_at"])

    # Calculate statistics
    success_rate = len(solutions_found) / num_trials
    avg_iterations = sum(solutions_found) / len(solutions_found) if solutions_found else float('inf')
    min_iterations = min(solutions_found) if solutions_found else None
    max_iterations_found = max(solutions_found) if solutions_found else None

    print(f"\n{'='*60}")
    print("ITERATIVE REFINEMENT TRIAL RESULTS")
    print('='*60)
    print(f"Trials: {num_trials}")
    print(f"Max iterations per trial: {max_iterations}")
    print(f"Success rate: {success_rate:.1%} ({len(solutions_found)}/{num_trials})")
    if solutions_found:
        print(f"Avg iterations to solution: {avg_iterations:.1f}")
        print(f"Min iterations: {min_iterations}")
        print(f"Max iterations: {max_iterations_found}")
    print('='*60)

    # Save summary
    summary = {
        "config": {
            "num_trials": num_trials,
            "max_iterations": max_iterations,
        },
        "summary": {
            "success_rate": success_rate,
            "avg_iterations_to_solution": avg_iterations if solutions_found else None,
            "min_iterations": min_iterations,
            "max_iterations": max_iterations_found,
            "solutions_found": len(solutions_found),
        },
        "trials": results,
    }

    with open("iterative_trials_results.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to: iterative_trials_results.json")

    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=10, help="Number of trials")
    parser.add_argument("--iterations", type=int, default=100, help="Max iterations per trial")
    args = parser.parse_args()

    run_trials(num_trials=args.trials, max_iterations=args.iterations)
