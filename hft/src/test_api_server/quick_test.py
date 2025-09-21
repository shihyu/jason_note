#!/usr/bin/env python3
"""Quick test script to verify gnuplot integration with smaller dataset"""

import subprocess
import sys
import os

# Import the functions from compare_performance
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compare_performance import run_test, write_data_files, generate_plots

def main():
    print("=" * 60)
    print("Quick Performance Test with Gnuplot Visualization")
    print("=" * 60)

    # Check if server is running
    try:
        result = subprocess.run(["curl", "-s", "http://localhost:8080/stats"],
                              capture_output=True, text=True, timeout=2)
        if result.returncode != 0:
            print("Error: API server is not running")
            sys.exit(1)
    except:
        print("Error: Cannot connect to API server")
        sys.exit(1)

    # Test configuration - smaller for quick test
    NUM_ORDERS = 100
    NUM_CONNECTIONS = 10
    WARMUP = 10
    NUM_TESTS = 2

    print(f"\nConfiguration:")
    print(f"  Orders per test: {NUM_ORDERS}")
    print(f"  Concurrent connections: {NUM_CONNECTIONS}")
    print(f"  Warmup orders: {WARMUP}")
    print(f"  Number of test runs: {NUM_TESTS}\n")

    results_data = []

    # Test Python client only for quick test
    print("Testing Python Client...")
    python_cmd = f"python3 python_client.py --orders {NUM_ORDERS} --connections {NUM_CONNECTIONS} --warmup {WARMUP}"
    python_results = run_test("Python", python_cmd, NUM_TESTS)

    if python_results:
        results_data.append({
            'client': 'Python (aiohttp)',
            'average': python_results['average'],
            'all_runs': python_results['all_runs']
        })
        print(f"✓ Python test completed - Throughput: {python_results['average'].get('throughput', 0):.0f} req/s")

    # Test C client
    print("\nTesting C Client...")
    c_cmd = f"./c-client/c_client {NUM_ORDERS} {NUM_CONNECTIONS} {WARMUP}"
    c_results = run_test("C", c_cmd, NUM_TESTS)

    if c_results:
        results_data.append({
            'client': 'C (libcurl)',
            'average': c_results['average'],
            'all_runs': c_results['all_runs']
        })
        print(f"✓ C test completed - Throughput: {c_results['average'].get('throughput', 0):.0f} req/s")

    # Generate data files and plots
    if results_data:
        print("\n" + "=" * 60)
        print("Generating Performance Data and Plots...")
        print("=" * 60)

        write_data_files(results_data)
        print("✓ Data files written to performance_data/")

        generate_plots()

        # List generated files
        if os.path.exists('performance_plots'):
            plots = os.listdir('performance_plots')
            if plots:
                print("\n✓ Generated plots:")
                for plot in sorted(plots):
                    print(f"  - performance_plots/{plot}")

        if os.path.exists('performance_data'):
            data_files = os.listdir('performance_data')
            if data_files:
                print("\n✓ Generated data files:")
                for data_file in sorted(data_files):
                    print(f"  - performance_data/{data_file}")

    print("\n" + "=" * 60)
    print("Quick test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
