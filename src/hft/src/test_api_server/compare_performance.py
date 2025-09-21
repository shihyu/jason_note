#!/usr/bin/env python3

import subprocess
import time
import sys
import json
import os
from tabulate import tabulate

def run_test(client_name, command, num_tests=3):
    """Run performance test multiple times and collect stats"""
    results = []

    for i in range(num_tests):
        print(f"Running {client_name} test {i+1}/{num_tests}...")

        # Clear server stats first
        subprocess.run(["curl", "-s", "http://localhost:8080/stats"],
                      capture_output=True)

        # Run the client test
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Parse output for metrics
        output = result.stdout

        # Extract metrics from output with improved error handling
        metrics = {}
        for line in output.split('\n'):
            try:
                # Normalize line for easier parsing
                line_lower = line.lower()
                parts = line.split()

                if 'throughput:' in line_lower and len(parts) >= 2:
                    # Try to extract number from second position
                    for part in parts[1:]:
                        try:
                            metrics['throughput'] = float(part)
                            break
                        except ValueError:
                            continue

                elif 'min latency:' in line_lower or ('min:' in line_lower and 'latency' in output.lower()):
                    # Extract min latency - try different positions
                    for part in parts[1:]:
                        try:
                            val = float(part)
                            if val > 0:  # Sanity check
                                metrics['min_latency'] = val
                                break
                        except ValueError:
                            continue

                elif 'max latency:' in line_lower or ('max:' in line_lower and 'latency' in output.lower()):
                    # Extract max latency
                    for part in parts[1:]:
                        try:
                            val = float(part)
                            if val > 0:
                                metrics['max_latency'] = val
                                break
                        except ValueError:
                            continue

                elif 'avg latency:' in line_lower:
                    # Extract average latency from "Avg latency: X.XX ms" format
                    for part in parts[2:]:  # Start from index 2 for "Avg latency:"
                        try:
                            val = float(part)
                            if val > 0:
                                metrics['avg_latency'] = val
                                break
                        except ValueError:
                            continue
                elif 'average:' in line_lower and 'latency' in output.lower():
                    # Extract from Go format "Average: X.XXX"
                    for part in parts[1:]:  # Start from index 1 for "Average:"
                        try:
                            val = float(part)
                            if val > 0:
                                metrics['avg_latency'] = val
                                break
                        except ValueError:
                            continue

                # Percentile extraction with flexible matching
                for percentile in [50, 90, 95, 99]:
                    p_key = f'p{percentile}'
                    p_patterns = [f'p{percentile}:', f'latency p{percentile}:']

                    for pattern in p_patterns:
                        if pattern in line_lower and p_key not in metrics:
                            for part in parts[1:]:
                                try:
                                    val = float(part)
                                    if val > 0:
                                        metrics[p_key] = val
                                        break
                                except ValueError:
                                    continue

            except Exception as e:
                # Log parsing error but continue
                print(f"Warning: Error parsing line '{line}': {e}", file=sys.stderr)

        if metrics:
            results.append(metrics)

        time.sleep(2)  # Wait between tests

    # Calculate averages
    if results:
        avg_metrics = {}
        for key in results[0].keys():
            avg_metrics[key] = sum(r.get(key, 0) for r in results) / len(results)
        return {'average': avg_metrics, 'all_runs': results}
    return None

def write_data_files(results_data):
    """Write data files for gnuplot"""
    # Create performance_data directory if it doesn't exist
    os.makedirs('performance_data', exist_ok=True)

    # Write throughput data
    with open('performance_data/throughput.dat', 'w') as f:
        f.write("# Client Throughput(req/s) StdDev\n")
        for client_data in results_data:
            client = client_data['client']
            runs = client_data['all_runs']
            throughputs = [r.get('throughput', 0) for r in runs]
            avg = sum(throughputs) / len(throughputs) if throughputs else 0
            # Use sample standard deviation for small sample sizes
            if len(throughputs) > 1:
                std = (sum([(x - avg) ** 2 for x in throughputs]) / (len(throughputs) - 1)) ** 0.5
            elif len(throughputs) == 1:
                std = 0
            else:
                std = 0
            f.write(f'"{client}" {avg:.2f} {std:.2f}\n')

    # Write latency percentiles data
    with open('performance_data/latency_percentiles.dat', 'w') as f:
        f.write("# Client P50 P90 P95 P99\n")
        for client_data in results_data:
            client = client_data['client']
            avg = client_data['average']
            f.write(f'"{client}" {avg.get("p50", 0):.2f} {avg.get("p90", 0):.2f} '
                   f'{avg.get("p95", 0):.2f} {avg.get("p99", 0):.2f}\n')

    # Write latency comparison data
    with open('performance_data/latency_comparison.dat', 'w') as f:
        f.write("# Client Min Avg Max\n")
        for client_data in results_data:
            client = client_data['client']
            avg = client_data['average']
            f.write(f'"{client}" {avg.get("min_latency", 0):.2f} '
                   f'{avg.get("avg_latency", 0):.2f} {avg.get("max_latency", 0):.2f}\n')

    # Write run-by-run data for time series
    with open('performance_data/time_series.dat', 'w') as f:
        f.write("# Run")
        for client_data in results_data:
            f.write(f' {client_data["client"]}_Throughput {client_data["client"]}_Latency')
        f.write("\n")

        max_runs = max(len(cd['all_runs']) for cd in results_data)
        for i in range(max_runs):
            f.write(f"{i+1}")
            for client_data in results_data:
                runs = client_data['all_runs']
                if i < len(runs):
                    f.write(f" {runs[i].get('throughput', 0):.2f} {runs[i].get('avg_latency', 0):.2f}")
                else:
                    f.write(" 0 0")
            f.write("\n")

    # Write summary statistics for table
    with open('performance_data/summary_stats.dat', 'w') as f:
        f.write("# Client Throughput(req/s) AvgLatency(ms) P50(ms) P95(ms) P99(ms)\n")
        for client_data in results_data:
            client = client_data['client']
            avg = client_data['average']
            f.write(f'"{client}" {avg.get("throughput", 0):.0f} '
                   f'{avg.get("avg_latency", 0):.2f} '
                   f'{avg.get("p50", 0):.2f} '
                   f'{avg.get("p95", 0):.2f} '
                   f'{avg.get("p99", 0):.2f}\n')

def generate_plots():
    """Generate plots using gnuplot"""
    print("\nGenerating performance plots with gnuplot...")

    # Check if gnuplot is installed
    try:
        subprocess.run(["gnuplot", "--version"], capture_output=True, check=True)
    except:
        print("Warning: gnuplot not found. Skipping plot generation.")
        print("Install with: sudo apt-get install gnuplot (Ubuntu) or brew install gnuplot (macOS)")
        return

    # Run gnuplot scripts
    try:
        subprocess.run(["gnuplot", "performance_plots.gnuplot"], check=True)
        print("Plots generated successfully in performance_plots/ directory")
    except subprocess.CalledProcessError:
        print("Warning: Failed to generate plots")
    except FileNotFoundError:
        print("Warning: performance_plots.gnuplot not found")

def main():
    print("=" * 80)
    print("Performance Comparison Test")
    print("=" * 80)
    print()
    
    # Check if server is running
    try:
        result = subprocess.run(["curl", "-s", "http://localhost:8080/stats"], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode != 0:
            print("Error: API server is not running on port 8080")
            print("Please start it with: cd rust-api-server && cargo run --release")
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: Cannot connect to API server")
        sys.exit(1)
    
    # Test configuration
    NUM_ORDERS = 5000
    NUM_CONNECTIONS = 100
    WARMUP = 500
    NUM_TESTS = 3
    
    print(f"Configuration:")
    print(f"  Orders per test: {NUM_ORDERS}")
    print(f"  Concurrent connections: {NUM_CONNECTIONS}")
    print(f"  Warmup orders: {WARMUP}")
    print(f"  Number of test runs per client: {NUM_TESTS}")
    print()
    
    # Run tests for each client
    results = []
    results_data = []  # For storing detailed results
    
    # Python client
    print("\n" + "=" * 40)
    print("Testing Python Client (aiohttp)")
    print("=" * 40)
    python_cmd = f"python3 python_client.py --orders {NUM_ORDERS} --connections {NUM_CONNECTIONS} --warmup {WARMUP}"
    python_results = run_test("Python", python_cmd, NUM_TESTS)
    if python_results:
        python_results['average']['client'] = 'Python (aiohttp)'
        results.append(python_results['average'])
        results_data.append({'client': 'Python (aiohttp)', 'average': python_results['average'], 'all_runs': python_results['all_runs']})
    
    # C client
    print("\n" + "=" * 40)
    print("Testing C Client (libcurl)")
    print("=" * 40)
    c_cmd = f"./c-client/c_client {NUM_ORDERS} {NUM_CONNECTIONS} {WARMUP}"
    c_results = run_test("C", c_cmd, NUM_TESTS)
    if c_results:
        c_results['average']['client'] = 'C (libcurl)'
        results.append(c_results['average'])
        results_data.append({'client': 'C (libcurl)', 'average': c_results['average'], 'all_runs': c_results['all_runs']})
    
    # C++ client
    print("\n" + "=" * 40)
    print("Testing C++ Client (libcurl)")
    print("=" * 40)
    cpp_cmd = f"./cpp-client/cpp_client {NUM_ORDERS} {NUM_CONNECTIONS} {WARMUP}"
    cpp_results = run_test("C++", cpp_cmd, NUM_TESTS)
    if cpp_results:
        cpp_results['average']['client'] = 'C++ (libcurl)'
        results.append(cpp_results['average'])
        results_data.append({'client': 'C++ (libcurl)', 'average': cpp_results['average'], 'all_runs': cpp_results['all_runs']})
    
    # Rust client
    print("\n" + "=" * 40)
    print("Testing Rust Client (reqwest)")
    print("=" * 40)
    rust_cmd = f"./rust-client/target/release/rust-client --orders {NUM_ORDERS} --connections {NUM_CONNECTIONS} --warmup {WARMUP}"
    rust_results = run_test("Rust", rust_cmd, NUM_TESTS)
    if rust_results:
        rust_results['average']['client'] = 'Rust (reqwest)'
        results.append(rust_results['average'])
        results_data.append({'client': 'Rust (reqwest)', 'average': rust_results['average'], 'all_runs': rust_results['all_runs']})

    # Go client
    print("\n" + "=" * 40)
    print("Testing Go Client (net/http)")
    print("=" * 40)
    go_cmd = f"./go-client/go_client --orders {NUM_ORDERS} --connections {NUM_CONNECTIONS} --warmup {WARMUP}"
    go_results = run_test("Go", go_cmd, NUM_TESTS)
    if go_results:
        go_results['average']['client'] = 'Go (net/http)'
        results.append(go_results['average'])
        results_data.append({'client': 'Go (net/http)', 'average': go_results['average'], 'all_runs': go_results['all_runs']})

    # Display comparison table
    if results:
        print("\n" + "=" * 80)
        print("PERFORMANCE COMPARISON RESULTS (averaged over {} runs)".format(NUM_TESTS))
        print("=" * 80)
        
        # Prepare data for table
        table_data = []
        for r in results:
            table_data.append([
                r['client'],
                f"{r.get('throughput', 0):.0f}",
                f"{r.get('min_latency', 0):.2f}",
                f"{r.get('avg_latency', 0):.2f}",
                f"{r.get('p50', 0):.2f}",
                f"{r.get('p90', 0):.2f}",
                f"{r.get('p95', 0):.2f}",
                f"{r.get('p99', 0):.2f}",
                f"{r.get('max_latency', 0):.2f}"
            ])
        
        headers = ['Client', 'Throughput\n(req/s)', 'Min\n(ms)', 'Avg\n(ms)', 
                  'P50\n(ms)', 'P90\n(ms)', 'P95\n(ms)', 'P99\n(ms)', 'Max\n(ms)']
        
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # Determine winner
        print("\n" + "=" * 80)
        print("PERFORMANCE RANKING")
        print("=" * 80)
        
        # Sort by throughput
        sorted_results = sorted(results, key=lambda x: x.get('throughput', 0), reverse=True)
        
        for i, r in enumerate(sorted_results, 1):
            print(f"{i}. {r['client']}: {r.get('throughput', 0):.0f} req/s "
                  f"(Avg latency: {r.get('avg_latency', 0):.2f} ms)")
        
        print("\n" + "=" * 80)
        print("ANALYSIS")
        print("=" * 80)
        
        # Calculate relative performance
        if len(sorted_results) >= 2:
            best = sorted_results[0]
            print(f"\nBest performer: {best['client']}")
            print(f"Throughput: {best.get('throughput', 0):.0f} req/s")
            print(f"Average latency: {best.get('avg_latency', 0):.2f} ms")
            
            print("\nRelative performance:")
            for r in sorted_results[1:]:
                perf_ratio = (best.get('throughput', 1) / r.get('throughput', 1))
                latency_ratio = r.get('avg_latency', 1) / best.get('avg_latency', 1)
                print(f"  {best['client']} is {perf_ratio:.1f}x faster than {r['client']}")
                print(f"  {r['client']} has {latency_ratio:.1f}x higher latency than {best['client']}")

        # Write data files and generate plots
        if results_data:
            write_data_files(results_data)
            generate_plots()

    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80)

if __name__ == "__main__":
    main()
