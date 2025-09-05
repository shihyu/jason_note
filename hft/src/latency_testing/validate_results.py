#!/usr/bin/env python3

import sys
import json
import subprocess
import statistics
from typing import Dict, List, Tuple

class LatencyValidator:
    """Validates HFT latency test results against expected thresholds"""
    
    def __init__(self):
        # Expected latency thresholds (in nanoseconds)
        self.thresholds = {
            'map_insertion': {
                'mean': 1000,  # 1 microsecond
                'p99': 5000,   # 5 microseconds
                'max': 100000  # 100 microseconds
            },
            'unordered_map_insertion': {
                'mean': 500,
                'p99': 2000,
                'max': 50000
            },
            'memcpy_4kb': {
                'mean': 200,
                'p99': 500,
                'max': 5000
            },
            'heap_allocation': {
                'mean': 100,
                'p99': 500,
                'max': 10000
            },
            'memory_pool': {
                'mean': 50,
                'p99': 200,
                'max': 2000
            },
            'orderbook_add': {
                'mean': 500,
                'p99': 2000,
                'max': 20000
            },
            'orderbook_cancel': {
                'mean': 300,
                'p99': 1000,
                'max': 10000
            },
            'network_rtt_local': {
                'mean': 50000,   # 50 microseconds for local
                'p99': 100000,  # 100 microseconds
                'max': 500000   # 500 microseconds
            }
        }
        
        self.results = []
        
    def run_benchmark(self, binary: str, args: str = "") -> Dict:
        """Run a benchmark and parse results"""
        try:
            cmd = f"./bin/{binary} {args}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {'error': f"Failed to run {cmd}: {result.stderr}"}
            
            # Parse output for statistics
            output = result.stdout
            stats = self.parse_output(output)
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def parse_output(self, output: str) -> Dict:
        """Parse benchmark output for statistics"""
        stats = {}
        
        lines = output.split('\n')
        current_test = None
        
        for line in lines:
            if '===' in line and 'Statistics' in line:
                # Extract test name
                current_test = line.strip('= ').replace(' Statistics', '')
                stats[current_test] = {}
            
            elif current_test and ':' in line:
                # Parse statistic lines
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    # Extract numeric value
                    if 'ns' in value:
                        value = float(value.replace('ns', '').strip())
                        stats[current_test][key.lower()] = value
        
        return stats
    
    def validate_threshold(self, test_name: str, metric: str, value: float) -> Tuple[bool, str]:
        """Validate a metric against threshold"""
        if test_name not in self.thresholds:
            return True, f"No threshold defined for {test_name}"
        
        if metric not in self.thresholds[test_name]:
            return True, f"No threshold for {metric}"
        
        threshold = self.thresholds[test_name][metric]
        
        if value <= threshold:
            return True, f"✓ {metric}: {value:.2f}ns <= {threshold}ns"
        else:
            return False, f"✗ {metric}: {value:.2f}ns > {threshold}ns"
    
    def validate_results(self, results: Dict) -> bool:
        """Validate all test results"""
        all_passed = True
        
        print("\n" + "="*50)
        print("         LATENCY VALIDATION RESULTS")
        print("="*50)
        
        for test_name, stats in results.items():
            if 'error' in stats:
                print(f"\n{test_name}: ERROR - {stats['error']}")
                all_passed = False
                continue
            
            print(f"\n{test_name}:")
            test_passed = True
            
            for metric in ['mean', 'p99', 'max']:
                if metric in stats:
                    passed, msg = self.validate_threshold(
                        test_name.lower().replace(' ', '_'), 
                        metric, 
                        stats[metric]
                    )
                    print(f"  {msg}")
                    if not passed:
                        test_passed = False
            
            if not test_passed:
                all_passed = False
        
        return all_passed
    
    def generate_report(self, results: Dict) -> str:
        """Generate JSON report of results"""
        report = {
            'results': results,
            'thresholds': self.thresholds,
            'passed': self.validate_results(results)
        }
        
        return json.dumps(report, indent=2)
    
    def check_system_config(self) -> List[str]:
        """Check system configuration for HFT"""
        warnings = []
        
        try:
            # Check CPU governor
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor', 'r') as f:
                governor = f.read().strip()
                if governor != 'performance':
                    warnings.append(f"CPU governor is '{governor}', should be 'performance'")
            
            # Check huge pages
            with open('/proc/sys/vm/nr_hugepages', 'r') as f:
                hugepages = int(f.read().strip())
                if hugepages < 128:
                    warnings.append(f"Only {hugepages} huge pages allocated, recommend >= 128")
            
            # Check network buffer sizes
            with open('/proc/sys/net/core/rmem_max', 'r') as f:
                rmem = int(f.read().strip())
                if rmem < 134217728:
                    warnings.append(f"Network receive buffer is {rmem}, recommend >= 134217728")
            
        except Exception as e:
            warnings.append(f"Could not check system config: {e}")
        
        return warnings

def main():
    validator = LatencyValidator()
    
    # Check system configuration
    print("Checking system configuration...")
    warnings = validator.check_system_config()
    if warnings:
        print("\nSystem configuration warnings:")
        for warning in warnings:
            print(f"  ⚠ {warning}")
    else:
        print("✓ System configuration looks good")
    
    # Run benchmarks
    print("\nRunning benchmarks...")
    results = {}
    
    # Basic latency tests
    print("  - Basic latency tests...")
    basic_results = validator.run_benchmark("basic_latency")
    results.update(basic_results)
    
    # Order book tests
    print("  - Order book tests...")
    ob_results = validator.run_benchmark("orderbook_latency", "ops")
    results.update(ob_results)
    
    # Memory pool tests
    print("  - Memory pool tests...")
    mem_results = validator.run_benchmark("memory_pool", "strategies")
    results.update(mem_results)
    
    # Validate results
    passed = validator.validate_results(results)
    
    # Save report
    report = validator.generate_report(results)
    with open('latency_report.json', 'w') as f:
        f.write(report)
    print("\nReport saved to latency_report.json")
    
    # Exit code
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()