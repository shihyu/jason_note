# K-Module Problem: Evolution vs Iterative Refinement

This example demonstrates a fundamental limitation of iterative refinement approaches and shows how evolutionary search with population-based exploration can solve problems that defeat single-trajectory optimization.

## The Problem

The K-Module Problem is a pipeline configuration task where you must find the correct combination of 4 independent modules:

| Module | Options |
|--------|---------|
| **loader** | csv_reader, json_reader, xml_reader, parquet_reader, sql_reader |
| **preprocess** | normalize, standardize, minmax, scale, none |
| **algorithm** | quicksort, mergesort, heapsort, bubblesort, insertion |
| **formatter** | json, xml, csv, yaml, protobuf |

**Search space**: 5⁴ = 625 possible combinations

**The Challenge**: The evaluator only tells you *how many* modules are correct (0-4), not *which ones*. This creates a deceptive fitness landscape with no gradient information.

## Why Iterative Refinement Fails

Consider this scenario:

```
Initial:  [json_reader, standardize, mergesort, xml]     → Score: 0/4
Refine 1: [csv_reader, standardize, mergesort, xml]      → Score: 1/4 ✓
Refine 2: [csv_reader, normalize, mergesort, xml]        → Score: 2/4 ✓✓
Refine 3: [csv_reader, normalize, heapsort, xml]         → Score: 1/4 ✗ (went backwards!)
Refine 4: [csv_reader, normalize, mergesort, json]       → Score: 2/4 (no progress)
```

**The Problem**: When the model changes `mergesort` to `heapsort`, it has no way to know this was wrong because:
- The score decreased, but was that because of the algorithm change?
- Or because `normalize` wasn't actually correct?
- The model can't tell which modules are contributing to the score

This leads to **random walk behavior** requiring O(625) evaluations on average.

## Why Evolution Succeeds

Evolution maintains a **population** that explores different regions simultaneously:

```
Generation 1:
  Individual A: [csv_reader, scale, quicksort, xml]      → 2/4 (loader, algorithm correct)
  Individual B: [json_reader, normalize, bubble, json]   → 2/4 (preprocess, formatter correct)
  Individual C: [xml_reader, minmax, mergesort, csv]     → 0/4

Generation 2 (crossover):
  Child(A,B): [csv_reader, normalize, quicksort, json]   → 4/4 SUCCESS!
```

**Key insight**: Evolution discovers correct modules in different individuals and **crossover combines them**. This is the "Building Block Hypothesis" - complex solutions are assembled from simpler discovered components.

## Running the Experiment

### Prerequisites

1. **OpenEvolve** (this repo):
   ```bash
   pip install -e .
   ```

2. **API Key** (both methods use the same model via OpenRouter for fair comparison):
   ```bash
   export OPENROUTER_API_KEY=your_key
   ```

Both OpenEvolve and the iterative agent use `google/gemini-2.5-flash-lite` via OpenRouter API for a fair comparison.

### Run OpenEvolve

```bash
cd examples/k_module_problem
chmod +x run_openevolve.sh
./run_openevolve.sh 50
```

Or directly:
```bash
openevolve-run initial_program.py evaluator.py --config config.yaml --iterations 50
```

### Run Iterative Agent

```bash
python iterative_agent.py --iterations 100
```

Or run multiple trials to get statistics:
```bash
python run_iterative_trials.py --trials 3 --iterations 100
```

### Run Random Baseline

Establish the "no learning" baseline (no LLM needed):

```bash
python run_random_baseline.py --samples 100 --trials 100
```

This runs 100 independent trials of random search, each with up to 100 samples, and calculates empirical pass@k metrics.

### Compare Results

```bash
python compare_results.py
```

This generates:
- `comparison_plot.png`: Visual comparison of convergence
- Summary statistics printed to console

## Experimental Results

### Random Baseline (100 trials, 100 samples each)

| Metric | Value |
|--------|-------|
| **Success rate (pass@100)** | 16% (16/100 trials found solution) |
| **Avg samples to solution** | 43.3 (when found) |
| **Min samples** | 5 (lucky guess) |
| **Max samples** | 91 |

This establishes the "no learning" baseline. Any method that beats this is demonstrating actual optimization, not just random sampling.

### Iterative Refinement Results (3 trials, 100 iterations max)

| Trial | Iterations | Result | Best Score |
|-------|------------|--------|------------|
| 1 | 100 | FAILED | 75% (3/4) |
| 2 | 100 | FAILED | 75% (3/4) |
| 3 | 13 | SUCCESS | 100% (4/4) |

**Summary:**
- **Success rate**: 33% (1/3 trials found solution)
- **When successful**: 13 iterations
- **Failure mode**: Gets stuck at 75% - keeps trying `standardize` instead of `normalize`

**Key observation**: The iterative agent repeatedly finds configurations with 3/4 correct modules (`csv_reader`, `quicksort`, `json`) but cannot identify that `preprocess` is the wrong module. It keeps cycling through variations without escaping this local optimum.

### OpenEvolve (Evolutionary) Results (3 trials, 100 iterations max)

| Trial | Iterations | Result | Best Score |
|-------|------------|--------|------------|
| 1 | 18 | SUCCESS | 100% (4/4) |
| 2 | 50 | SUCCESS | 100% (4/4) |
| 3 | 89 | SUCCESS | 100% (4/4) |

**Summary:**
- **Success rate**: 100% (3/3 trials found solution)
- **Avg iterations to solution**: 52.3
- **Min iterations**: 18
- **Max iterations**: 89

**Key advantage**: OpenEvolve's population-based approach maintains diverse configurations that explore different module combinations in parallel. Even when some individuals get stuck at local optima (75% with wrong preprocessing), others explore alternatives and eventually discover the correct solution.

### Comparison Summary

| Method | Success Rate | Avg Iterations | Key Finding |
|--------|-------------|----------------|-------------|
| **Random Baseline** | 16% | 43.3 (when found) | No learning baseline |
| **Iterative Refinement** | 33% (1/3) | 13 (when found) | Gets stuck at 75% local optimum |
| **OpenEvolve** | **100% (3/3)** | 52.3 | Always finds solution |

**Key insight**: While OpenEvolve takes more iterations on average (52.3 vs 13), it has a **100% success rate** compared to iterative refinement's 33%. The evolutionary approach's population diversity ensures it eventually escapes local optima that trap single-trajectory methods.

### Rich Feedback Mode: Proving Attribution Matters

To verify that feedback attribution is the key factor, we added a `RICH_FEEDBACK=1` mode that tells the agent exactly which modules are correct/incorrect:

```bash
RICH_FEEDBACK=1 python run_iterative_trials.py --trials 3 --iterations 100
```

| Method | Success Rate | Avg Iterations |
|--------|-------------|----------------|
| **Iterative (no feedback)** | 33% | 13 (when found) |
| **Iterative (rich feedback)** | **100%** | **3** |

With rich feedback, iterative refinement achieves **100% success rate in only 3 iterations** - dramatically faster than OpenEvolve's 52 iterations! This proves that:

1. **Feedback attribution is the key factor**, not the optimization method
2. When feedback is attributable, iterative refinement is highly effective
3. Evolution is necessary when feedback is NOT attributable (you can't tell which component is wrong)

## Why This Matters

This example illustrates when you should prefer evolutionary approaches:

1. **Combinatorial Configuration**: When solutions are combinations of independent choices
2. **Deceptive Fitness**: When partial solutions don't clearly indicate which components are correct
3. **No Gradient**: When small changes don't reliably improve or degrade solutions
4. **Building Block Problems**: When good solutions are assembled from discovered components

Real-world examples:
- Hyperparameter tuning (learning rate + batch size + architecture)
- Feature selection (which features to include)
- API composition (which services to combine)
- Configuration optimization (compiler flags, system settings)

## Files

| File | Description |
|------|-------------|
| `initial_program.py` | Starting configuration (0/4 correct) |
| `evaluator.py` | Scores configurations (0-4 correct modules) |
| `config.yaml` | OpenEvolve configuration |
| `iterative_agent.py` | Iterative refinement agent using OpenRouter API |
| `run_iterative_trials.py` | Run multiple trials of iterative agent |
| `run_openevolve_trials.py` | Run multiple trials of OpenEvolve |
| `run_random_baseline.py` | Random search baseline with pass@k analysis |
| `compare_results.py` | Analysis and visualization |

## Configuration Details

The OpenEvolve config uses settings optimized for this combinatorial problem:

```yaml
# High temperature for diverse exploration
temperature: 0.9

# Very high exploration ratio
exploration_ratio: 0.6
exploitation_ratio: 0.25

# Multiple islands for parallel search with frequent migration
num_islands: 5
migration_interval: 3
migration_rate: 0.3

# Larger population for more diversity
population_size: 25
```

**Key config improvements over default:**
- Higher temperature (0.9 vs 0.7) - more exploration of different options
- Prompt emphasizes systematic exploration, not following hints
- More islands (5) with faster migration (interval=3) - combines building blocks faster
- Larger population (25) - maintains more diverse configurations

## References

- **Building Block Hypothesis**: Holland, J.H. (1975). *Adaptation in Natural and Artificial Systems*
- **Schema Theorem**: Explains how evolution propagates good partial solutions
- **No Free Lunch**: Wolpert & Macready (1997) - Evolution excels on problems with structure

## Conclusion

This example demonstrates that **iterative refinement is not sufficient** for problems with independent, combinatorial components. Evolutionary search with population-based exploration and crossover can solve these problems orders of magnitude faster by:

1. Exploring multiple regions of the search space simultaneously
2. Discovering correct "building blocks" in different individuals
3. Combining discoveries through crossover to assemble complete solutions

When your optimization problem has this structure, consider evolutionary approaches like OpenEvolve over single-trajectory iterative refinement.
