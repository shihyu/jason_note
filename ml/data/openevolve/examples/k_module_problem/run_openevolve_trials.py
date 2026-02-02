#!/usr/bin/env python3
"""Run multiple trials of OpenEvolve to get statistics."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Run from the example directory
os.chdir(Path(__file__).parent)


def run_trial(trial_num: int, max_iterations: int = 100, seed: int = None):
    """Run a single OpenEvolve trial."""
    output_dir = f"openevolve_output_trial_{trial_num}"

    # Clean output directory
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # Update config with new seed if provided
    if seed is not None:
        # Read config
        with open("config.yaml", "r") as f:
            config_content = f.read()

        # Replace seed
        import re
        config_content = re.sub(r'random_seed:\s*\d+', f'random_seed: {seed}', config_content)

        # Write temp config
        temp_config = f"config_trial_{trial_num}.yaml"
        with open(temp_config, "w") as f:
            f.write(config_content)
    else:
        temp_config = "config.yaml"

    # Run OpenEvolve
    cmd = [
        "openevolve-run",
        "initial_program.py",
        "evaluator.py",
        "--config", temp_config,
        "--iterations", str(max_iterations),
        "--output", output_dir,
    ]

    print(f"\n{'='*60}")
    print(f"TRIAL {trial_num + 1}: Running OpenEvolve with seed {seed}")
    print('='*60)

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Clean up temp config
    if seed is not None and os.path.exists(temp_config):
        os.remove(temp_config)

    # Parse results from log
    solution_found_at = None
    best_score = 0.0

    log_dir = Path(output_dir) / "logs"
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            with open(log_files[0], "r") as f:
                log_content = f.read()

            import re

            # Find best score
            score_matches = re.findall(r'combined_score[=:]\s*([\d.]+)', log_content)
            if score_matches:
                best_score = max(float(s) for s in score_matches)

            # Look for first 100% solution - find the "New best" line with 1.0000
            new_best_matches = re.findall(r'New best solution found at iteration (\d+):', log_content)
            perfect_matches = re.findall(r'Iteration (\d+):.*?combined_score=1\.0000', log_content)

            if perfect_matches:
                solution_found_at = int(perfect_matches[0])
            elif best_score >= 1.0 and new_best_matches:
                # Fallback: find last new best if we have 100%
                solution_found_at = int(new_best_matches[-1])

    return {
        "trial": trial_num,
        "seed": seed,
        "solution_found_at": solution_found_at,
        "best_score": best_score,
        "max_iterations": max_iterations,
    }


def run_trials(num_trials: int = 3, max_iterations: int = 100, base_seed: int = 100):
    """Run multiple trials and collect statistics."""
    results = []
    solutions_found = []

    for trial in range(num_trials):
        seed = base_seed + trial * 111  # Different seeds for each trial
        result = run_trial(trial, max_iterations, seed)
        results.append(result)

        if result["solution_found_at"] is not None:
            solutions_found.append(result["solution_found_at"])
            print(f"Trial {trial + 1}: SUCCESS at iteration {result['solution_found_at']}")
        else:
            print(f"Trial {trial + 1}: FAILED (best score: {result['best_score']:.2%})")

    # Calculate statistics
    success_rate = len(solutions_found) / num_trials
    avg_iterations = sum(solutions_found) / len(solutions_found) if solutions_found else float('inf')
    min_iterations = min(solutions_found) if solutions_found else None
    max_iterations_found = max(solutions_found) if solutions_found else None

    print(f"\n{'='*60}")
    print("OPENEVOLVE TRIAL RESULTS")
    print('='*60)
    print(f"Trials: {num_trials}")
    print(f"Max iterations per trial: {max_iterations}")
    print(f"Success rate: {success_rate:.0%} ({len(solutions_found)}/{num_trials})")
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

    with open("openevolve_trials_results.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to: openevolve_trials_results.json")

    # Clean up trial output directories
    for trial in range(num_trials):
        output_dir = f"openevolve_output_trial_{trial}"
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=3, help="Number of trials")
    parser.add_argument("--iterations", type=int, default=100, help="Max iterations per trial")
    parser.add_argument("--seed", type=int, default=100, help="Base random seed")
    args = parser.parse_args()

    run_trials(num_trials=args.trials, max_iterations=args.iterations, base_seed=args.seed)
