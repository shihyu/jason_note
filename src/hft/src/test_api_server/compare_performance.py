#!/usr/bin/env python3

import subprocess
import json
import time
import sys
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
        
        # Extract metrics from output
        metrics = {}
        for line in output.split('\n'):
            if 'Throughput:' in line:
                metrics['throughput'] = float(line.split()[1])
            elif 'Min latency:' in line:
                metrics['min_latency'] = float(line.split()[2])
            elif 'Max latency:' in line:
                metrics['max_latency'] = float(line.split()[2])
            elif 'Avg latency:' in line:
                metrics['avg_latency'] = float(line.split()[2])
            elif 'P50:' in line:
                metrics['p50'] = float(line.split()[1])
            elif 'P90:' in line:
                metrics['p90'] = float(line.split()[1])
            elif 'P95:' in line:
                metrics['p95'] = float(line.split()[1])
            elif 'P99:' in line:
                metrics['p99'] = float(line.split()[1])
        
        if metrics:
            results.append(metrics)
        
        time.sleep(2)  # Wait between tests
    
    # Calculate averages
    if results:
        avg_metrics = {}
        for key in results[0].keys():
            avg_metrics[key] = sum(r.get(key, 0) for r in results) / len(results)
        return avg_metrics
    return None

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
    
    # Python client
    print("\n" + "=" * 40)
    print("Testing Python Client (aiohttp)")
    print("=" * 40)
    python_cmd = f"python3 python_client.py --orders {NUM_ORDERS} --connections {NUM_CONNECTIONS} --warmup {WARMUP}"
    python_results = run_test("Python", python_cmd, NUM_TESTS)
    if python_results:
        python_results['client'] = 'Python (aiohttp)'
        results.append(python_results)
    
    # C++ client
    print("\n" + "=" * 40)
    print("Testing C++ Client (libcurl)")
    print("=" * 40)
    cpp_cmd = f"./cpp-client/cpp_client {NUM_ORDERS} {NUM_CONNECTIONS} {WARMUP}"
    cpp_results = run_test("C++", cpp_cmd, NUM_TESTS)
    if cpp_results:
        cpp_results['client'] = 'C++ (libcurl)'
        results.append(cpp_results)
    
    # Rust client
    print("\n" + "=" * 40)
    print("Testing Rust Client (reqwest)")
    print("=" * 40)
    rust_cmd = f"./rust-client/target/release/rust-client --orders {NUM_ORDERS} --connections {NUM_CONNECTIONS} --warmup {WARMUP}"
    rust_results = run_test("Rust", rust_cmd, NUM_TESTS)
    if rust_results:
        rust_results['client'] = 'Rust (reqwest)'
        results.append(rust_results)
    
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
    
    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80)

if __name__ == "__main__":
    main()