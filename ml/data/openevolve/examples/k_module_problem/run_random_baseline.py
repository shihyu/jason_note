#!/usr/bin/env python3
"""
Random Baseline for K-Module Problem

This script establishes a baseline by randomly sampling configurations.
It simulates what you'd get with pass@N (N independent random attempts)
without any learning or optimization.

This is useful because:
1. It establishes the "no learning" baseline
2. For closed models that don't support n>1 responses, we can't do true pass@k
3. Shows the expected performance of random search

Usage:
    python run_random_baseline.py [--samples 100] [--trials 10]
"""

import argparse
import json
import random
import time
from pathlib import Path

# Import the evaluator
from evaluator import VALID_OPTIONS, CORRECT_CONFIG, NUM_MODULES


def generate_random_config() -> dict:
    """Generate a random pipeline configuration."""
    return {
        module: random.choice(options)
        for module, options in VALID_OPTIONS.items()
    }


def score_config(config: dict) -> int:
    """Score a configuration (number of correct modules)."""
    return sum(
        1 for module, value in config.items()
        if CORRECT_CONFIG.get(module) == value
    )


def run_random_search(max_samples: int) -> dict:
    """
    Run random search until solution found or max_samples reached.

    Returns:
        dict with results
    """
    results = {
        "samples": [],
        "scores": [],
        "best_scores": [],
        "solution_found_at": None,
        "configs_tried": [],
    }

    best_so_far = 0

    for i in range(max_samples):
        config = generate_random_config()
        score = score_config(config)

        results["samples"].append(i)
        results["scores"].append(score / NUM_MODULES)
        best_so_far = max(best_so_far, score)
        results["best_scores"].append(best_so_far / NUM_MODULES)
        results["configs_tried"].append(config)

        if score == NUM_MODULES and results["solution_found_at"] is None:
            results["solution_found_at"] = i

    return results


def run_multiple_trials(num_trials: int, max_samples: int) -> list:
    """Run multiple independent trials of random search."""
    trial_results = []

    for trial in range(num_trials):
        random.seed(trial * 1000 + int(time.time()))  # Different seed per trial
        result = run_random_search(max_samples)
        trial_results.append({
            "trial": trial,
            "solution_found_at": result["solution_found_at"],
            "final_best_score": result["best_scores"][-1] if result["best_scores"] else 0,
            "scores": result["scores"],
            "best_scores": result["best_scores"],
        })

    return trial_results


def calculate_pass_at_k(trial_results: list, k_values: list) -> dict:
    """
    Calculate pass@k metrics.

    pass@k = probability of finding solution within k samples

    For random search on 625 possibilities:
    - pass@1 = 1/625 = 0.16%
    - pass@100 ≈ 1 - (624/625)^100 ≈ 14.8%
    - pass@312 ≈ 50% (half the search space)
    """
    pass_at_k = {}

    for k in k_values:
        successes = sum(
            1 for r in trial_results
            if r["solution_found_at"] is not None and r["solution_found_at"] < k
        )
        pass_at_k[k] = successes / len(trial_results)

    return pass_at_k


def theoretical_pass_at_k(k: int, search_space: int = 625) -> float:
    """Calculate theoretical pass@k for uniform random search."""
    # Probability of NOT finding solution in k tries
    prob_fail = ((search_space - 1) / search_space) ** k
    return 1 - prob_fail


def main():
    parser = argparse.ArgumentParser(description="Random baseline for K-Module problem")
    parser.add_argument("--samples", type=int, default=100, help="Max samples per trial")
    parser.add_argument("--trials", type=int, default=100, help="Number of independent trials")
    parser.add_argument("--output", default="random_baseline_output", help="Output directory")
    args = parser.parse_args()

    print("=" * 60)
    print("K-MODULE PROBLEM: RANDOM BASELINE")
    print("=" * 60)
    print(f"Search space: {5**NUM_MODULES} configurations")
    print(f"Running {args.trials} trials with up to {args.samples} samples each")
    print()

    # Run trials
    print("Running random search trials...")
    trial_results = run_multiple_trials(args.trials, args.samples)

    # Calculate statistics
    solutions_found = [r for r in trial_results if r["solution_found_at"] is not None]
    success_rate = len(solutions_found) / len(trial_results)

    if solutions_found:
        avg_samples_to_solution = sum(r["solution_found_at"] for r in solutions_found) / len(solutions_found)
        min_samples = min(r["solution_found_at"] for r in solutions_found)
        max_samples = max(r["solution_found_at"] for r in solutions_found)
    else:
        avg_samples_to_solution = float('inf')
        min_samples = max_samples = None

    # Calculate pass@k
    k_values = [1, 10, 20, 50, 100, 200, 312]
    k_values = [k for k in k_values if k <= args.samples]
    empirical_pass_at_k = calculate_pass_at_k(trial_results, k_values)

    # Print results
    print("\n### Results")
    print(f"  Success rate: {success_rate:.1%} ({len(solutions_found)}/{len(trial_results)} trials)")
    if solutions_found:
        print(f"  Avg samples to solution: {avg_samples_to_solution:.1f}")
        print(f"  Min samples: {min_samples}")
        print(f"  Max samples: {max_samples}")
    else:
        print(f"  No solutions found in {args.samples} samples")

    print("\n### Pass@k Comparison (Empirical vs Theoretical)")
    print("  k     | Empirical | Theoretical")
    print("  ------|-----------|------------")
    for k in k_values:
        emp = empirical_pass_at_k.get(k, 0)
        theo = theoretical_pass_at_k(k)
        print(f"  {k:5d} | {emp:8.1%}  | {theo:8.1%}")

    # Save results
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    results = {
        "config": {
            "samples_per_trial": args.samples,
            "num_trials": args.trials,
            "search_space": 5 ** NUM_MODULES,
        },
        "summary": {
            "success_rate": success_rate,
            "avg_samples_to_solution": avg_samples_to_solution if solutions_found else None,
            "min_samples": min_samples,
            "max_samples": max_samples,
        },
        "pass_at_k": {
            "empirical": empirical_pass_at_k,
            "theoretical": {k: theoretical_pass_at_k(k) for k in k_values},
        },
        "trials": trial_results,
    }

    with open(output_dir / "random_baseline_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_dir}/random_baseline_results.json")

    # Key insight
    print("\n### Key Insight")
    print("  Random search requires ~312 samples (50% of search space) on average.")
    print("  This is the baseline that any optimization method should beat.")
    print("  ")
    print("  For LLM-based methods:")
    print("  - pass@k with closed models requires k separate API calls")
    print("  - Each call is independent (no learning across calls)")
    print("  - This is equivalent to random search if prompts don't help")
    print("  ")
    print("  OpenEvolve should find solutions in <<312 evaluations by:")
    print("  - Learning from population diversity")
    print("  - Combining good 'building blocks' via crossover")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
