# SLDBench — Scaling Law Discovery Benchmark

## Introduction

**SLDBench** is a benchmark for discovering scaling laws, originally introduced in the paper [*Can Language Models Discover Their Own Scaling Laws?*](https://arxiv.org/abs/2507.21184) by Lin et al. It aggregates over **5,000 LLM training experiments** from recent scaling-law literature into a unified dataset, hosted on the Hugging Face Hub at [`pkuHaowei/sldbench`](https://huggingface.co/datasets/pkuHaowei/sldbench). 

Also check this [blog](https://algorithmicsuperintelligence.ai/blog/openevolve-sldagent/) for quickly understanding OpenEvolve x SLDBench.

## Overview

SLDBench focuses on **discovery** rather than simple curve fitting. The agent must identify:

- A **symbolic law** $f_\theta(x)$ (the functional form).
- A **parameter fitting routine** that generalizes across multiple training scenarios.

**Key Features:**

- **Data Source:** All task data is pulled dynamically from the Hugging Face dataset.
- **Extrapolation Evaluation:** Models are trained on smaller-scale runs and strictly evaluated on held-out, larger-scale configurations to test predictive capability.
- **Evolutionary Loop:** OpenEvolve iteratively mutates and evaluates candidate implementations of `scaling_law_func(...)` (the symbolic law) and `fit_scaling_law(...)` (the optimizer).

------

## SLDBench Tasks

There are currently 7 core scaling-law discovery tasks, each derived from real-world LLM experiments. Configuration files for these tasks are located in `examples/sldbench/configs/`.

| **Task Name (Config)**           | **Scenario**                                 | **Inputs (X)**                                       | **Target (y)**                 |
| -------------------------------- | -------------------------------------------- | ---------------------------------------------------- | ------------------------------ |
| **parallel_scaling_law**         | Parallel / Best-of-N inference scaling.      | Model size $N$, Parallelism $P$                      | Loss $L(N, P)$                 |
| **vocab_scaling_law**            | Vocabulary size vs. model/data scaling.      | Non-vocab size $N$, Vocab size $V$, Dataset size $D$ | Unigram-normalized loss $L$    |
| **sft_scaling_law**              | Supervised Fine-Tuning (SFT).                | SFT dataset size $D$                                 | Fine-tuning loss $L(D)$        |
| **domain_mixture_scaling_law**   | Multi-domain pre-training mixtures.          | Domain mixture proportions $r$                       | Per-domain losses $\{L_i(r)\}$ |
| **moe_scaling_law**              | Mixture-of-Experts (MoE) scaling.            | Network size $N$, Experts $E$                        | Pre-training loss $L(N, E)$    |
| **data_constrained_scaling_law** | Data-constrained pre-training regimes.       | Model size $N$, Dataset size $D$, Unique tokens $U$  | Loss $L(N, D, U)$              |
| **lr_bsz_scaling_law**           | Joint Learning Rate / Batch Size (Step Law). | LR $l$, Batch size $b$, Dataset $D$, Model $N$       | Loss $L(l, b, D, N)$ & Optima  |

> **Note:** A task named `easy_question_scaling_law` is also included for U-shape scaling studies, though it is not part of the current paper reference.

------

## File Structure

- `configs/` — YAML configuration files defining data splits, features, targets, and evaluation settings for each task.
- `data_loader.py` — Unified data loader for the `pkuHaowei/sldbench` Hugging Face dataset.
- `evaluator.py` — The evaluation framework; handles data splitting (train/extrapolate) and metric computation.
- `init_program.py` — The seed implementation (a power-law–style baseline) to jumpstart the evolutionary search.

------

## Usage

### Configuration Prerequisites

Before running any tasks, ensure your API key environment variable is set for your API provider (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).

### Running Individual Tasks

To run the evolutionary process for a specific task:

```bash
python openevolve-run.py \
  examples/sldbench/init_program.py \
  examples/sldbench/evaluator.py \
  --config examples/sldbench/configs/sft_scaling_law.yaml \
  --api-base "https://api.openai.com/v1" \
  --iterations 50
```

To switch tasks, simply point the `--config` argument to a different YAML file found in `examples/sldbench/configs/`.

### Automated Benchmark Script

A complete benchmark script `run.sh` is provided for running multiple tasks across different models with parallelism:

```bash
cd examples/sldbench
chmod +x run.sh
./run.sh 4  # Run with parallelism degree of 4 per model
```

**Note**: Configure the `API_BASE` variable in the script (defaults to `https://api.openai.com/v1`) and ensure your API key environment variable is set.

The script handles evolution and evaluation automatically, storing results in `./results/`.

### Important: Test Set Evaluation

**Note:** The `openevolve-run` command only evaluates programs on the **training set** during evolution. To compute final metrics on the **test set**, you must explicitly run:

```bash
python evaluator.py "path/to/generated_program.py"
```

The `evaluator.py` script, when run in `__main__` mode, computes metrics on the held-out extrapolation test set, which is the proper way to evaluate the discovered scaling laws' predictive capability.

------

## Data Format & Evaluation

Each task is formulated as a scaling-law discovery problem containing:

1. **Features ($X$):** Input variables (e.g., $N, D, \text{LR}, \text{Batch Size}$).
2. **Targets ($y$):** Performance metrics (typically training or validation loss).
3. **Groups:** Control indices representing distinct experimental settings (e.g., different model architectures) that share the law *form* but require distinct fitted *parameters*.

### The Evaluation Process

1. **Splitting:** The evaluator partitions data into **training** and **extrapolation test** sets. The largest models or datasets are explicitly held out to mirror real-world forecasting needs.
2. **Fitting:** The `fit_scaling_law` function optimizes parameters on the training portion for each group.
3. **Scoring:** The fitted law is applied to the test set to compute the following metrics:

- **NMSE:** Normalized Mean Squared Error
- **NMAE:** Normalized Mean Absolute Error
- **$R^2$:** Coefficient of Determination
- **Combined Score:** A single scalar summary (currently equivalent to $R^2$).

*Higher combined scores indicate superior extrapolation quality.*

------

## Evolution Markers

OpenEvolve modifies code explicitly wrapped in evolution blocks. The agent evolves the symbolic form and the optimizer simultaneously:

Python

```
# EVOLVE-BLOCK-START
def scaling_law_func(data_points, params):
    # Returns predicted values given inputs and parameters
    pass

def fit_scaling_law(data_points, loss_values):
    # Optimizes parameters to fit the scaling law
    pass
# EVOLVE-BLOCK-END
```

The system mutates these blocks, evaluates them via `evaluator.py`, and maintains a database of the highest-performing implementations.

## Requirements

Bash

```
pip install datasets numpy scipy
# Ensure the latest version of openevolve is installed
```

## Citation

If you utilize SLDBench, this example, or derived results in your work, please cite the original paper:

```
@article{lin2025sldbench,
  title   = {Can Language Models Discover Scaling Laws?},
  author  = {Lin, Haowei and Ye, Haotian and Feng, Wenzheng and Huang, Quzhe and
             Li, Yujun and Lim, Hubert and Li, Zhengrui and Wang, Xiangyu and
             Ma, Jianzhu and Liang, Yitao and Zou, James},
  journal = {arXiv preprint arXiv:2507.21184},
  year    = {2025}
}
