# EVOLVE-BLOCK-START
"""
K-Module Pipeline Configuration Problem

This problem demonstrates a scenario where iterative refinement struggles
but evolutionary search with crossover excels.

The task is to find the correct configuration for a 4-component data
processing pipeline. Each module has 5 possible options, creating a
search space of 5^4 = 625 possible combinations.

The key challenge: there's no gradient information. Getting 3/4 modules
correct gives the same partial feedback as 1/4 - you don't know WHICH
modules are correct.
"""


def configure_pipeline():
    """
    Configure a data processing pipeline with 4 independent modules.

    Each module choice is independent - changing one doesn't affect
    what's optimal for others. This creates a "needle in haystack"
    problem for iterative refinement but is solvable efficiently
    by evolutionary crossover.

    Returns:
        dict: Configuration with keys 'loader', 'preprocess', 'algorithm', 'formatter'
    """
    # Available options for each module:
    # loader: ['csv_reader', 'json_reader', 'xml_reader', 'parquet_reader', 'sql_reader']
    # preprocess: ['normalize', 'standardize', 'minmax', 'scale', 'none']
    # algorithm: ['quicksort', 'mergesort', 'heapsort', 'bubblesort', 'insertion']
    # formatter: ['json', 'xml', 'csv', 'yaml', 'protobuf']

    # Initial guess - likely not optimal
    config = {
        'loader': 'json_reader',      # Try different loaders
        'preprocess': 'standardize',   # Try different preprocessing
        'algorithm': 'mergesort',      # Try different algorithms
        'formatter': 'xml',            # Try different formatters
    }

    return config


# EVOLVE-BLOCK-END


def run_pipeline():
    """Run the pipeline configuration (entry point for evaluator)."""
    return configure_pipeline()


if __name__ == "__main__":
    config = run_pipeline()
    print(f"Pipeline configuration: {config}")
