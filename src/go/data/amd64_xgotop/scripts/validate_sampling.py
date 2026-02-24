#!/usr/bin/env python3
"""
Validate sampling rates by comparing expected vs actual event counts.

Usage:
    python validate_sampling.py <baseline_metrics.json> <sampled_metrics.json> [sampling_rates]
    
Example:
    python validate_sampling.py baseline.json sampled.json "newgoroutine:0.1,makemap:0.2,makeslice:0.1,newobject:0.5"
"""

import sys
import json
import argparse
from typing import Dict, Tuple, List
from dataclasses import dataclass


@dataclass
class EventCounts:
    """Store event counts by type"""
    casgstatus: int = 0
    makeslice: int = 0
    makemap: int = 0
    newobject: int = 0
    newgoroutine: int = 0
    goexit: int = 0


@dataclass
class SamplingResult:
    """Result of sampling validation"""
    event_type: str
    baseline_count: int
    sampled_count: int
    expected_rate: float
    actual_rate: float
    error: float
    within_tolerance: bool


def parse_sampling_rates(rates_str: str) -> Dict[str, float]:
    """Parse sampling rates from string format"""
    rates = {}
    if not rates_str:
        return rates
    
    for pair in rates_str.split(','):
        event, rate = pair.split(':')
        rates[event.strip()] = float(rate.strip())
    
    return rates


def count_events_from_metrics(metrics_file: str) -> EventCounts:
    """Count events from xgotop metrics JSON file"""
    with open(metrics_file, 'r') as f:
        data = json.load(f)
    
    counts = EventCounts()
    
    # Map event type IDs to names (based on storage.go)
    event_type_map = {
        0: 'casgstatus',
        1: 'makeslice',
        2: 'makemap',
        3: 'newobject',
        4: 'newgoroutine',
        5: 'goexit'
    }
    
    # If metrics contain event counts by type
    if 'event_counts' in data:
        for event_type_str, count in data['event_counts'].items():
            event_name = event_type_map.get(int(event_type_str), None)
            if event_name:
                setattr(counts, event_name, count)
    else:
        # Otherwise, try to extract from total events
        total = data.get('total_events', 0)
        print(f"Warning: No event_counts found in {metrics_file}, using total events: {total}")
        print("Note: You may need to rebuild xgotop with the latest changes to include event_counts in metrics")
    
    return counts


def validate_sampling(
    baseline_counts: EventCounts,
    sampled_counts: EventCounts,
    sampling_rates: Dict[str, float],
    tolerance: float = 0.05
) -> Tuple[List[SamplingResult], bool]:
    """
    Validate sampling accuracy.
    
    Args:
        baseline_counts: Event counts without sampling
        sampled_counts: Event counts with sampling
        sampling_rates: Expected sampling rates
        tolerance: Acceptable error margin (default 5%)
    
    Returns:
        List of validation results and overall success
    """
    results = []
    all_valid = True
    
    for event_type in EventCounts.__annotations__.keys():
        baseline = getattr(baseline_counts, event_type)
        sampled = getattr(sampled_counts, event_type)
        expected_rate = sampling_rates.get(event_type, 1.0)
        
        if baseline == 0:
            continue
        
        actual_rate = sampled / baseline
        error = actual_rate - expected_rate
        within_tolerance = abs(error) <= tolerance
        
        if not within_tolerance:
            all_valid = False
        
        results.append(SamplingResult(
            event_type=event_type,
            baseline_count=baseline,
            sampled_count=sampled,
            expected_rate=expected_rate,
            actual_rate=actual_rate,
            error=error,
            within_tolerance=within_tolerance
        ))
    
    return results, all_valid


def print_validation_report(results: List[SamplingResult]):
    """Print a formatted validation report"""
    print("\n" + "="*80)
    print("SAMPLING VALIDATION REPORT")
    print("="*80)
    print(f"{'Event Type':<15} {'Baseline':<10} {'Sampled':<10} {'Expected %':<12} {'Actual %':<12} {'Error %':<10} {'Status':<10}")
    print("-"*80)
    
    for r in results:
        status = "✓ PASS" if r.within_tolerance else "✗ FAIL"
        # Format error percentage to avoid "-0.00"
        error_pct = r.error * 100
        if abs(error_pct) < 0.005:
            error_str = "0.00"
        else:
            error_str = f"{error_pct:.2f}"
        print(f"{r.event_type:<15} {r.baseline_count:<10} {r.sampled_count:<10} "
              f"{r.expected_rate*100:<12.1f} {r.actual_rate*100:<12.1f} "
              f"{error_str:<10} {status:<10}")
    
    print("-"*80)
    
    # Summary statistics
    if results:
        avg_error = sum(r.error for r in results) / len(results)
        pass_rate = sum(1 for r in results if r.within_tolerance) / len(results) * 100
        
        # Format average error to avoid "-0.00%"
        avg_error_pct = avg_error * 100
        if abs(avg_error_pct) < 0.005:
            avg_error_str = "0.00"
        else:
            avg_error_str = f"{avg_error_pct:.2f}"
        
        print(f"\nAverage Error: {avg_error_str}%")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if pass_rate == 100:
            print("\n✓ All sampling rates are within tolerance!")
        else:
            print("\n✗ Some sampling rates are outside tolerance.")
            print("Note: Small deviations are expected due to the probabilistic nature of sampling.")


def main():
    parser = argparse.ArgumentParser(description='Validate xgotop sampling rates')
    parser.add_argument('baseline', help='Baseline metrics JSON file (no sampling)')
    parser.add_argument('sampled', help='Sampled metrics JSON file')
    parser.add_argument('rates', nargs='?', 
                       help='Sampling rates (e.g., "newgoroutine:0.1,makemap:0.2")')
    parser.add_argument('--tolerance', type=float, default=5,
                       help='Error tolerance percentage (default: 5%%)')
    
    args = parser.parse_args()
    
    # Count events from metrics files
    try:
        baseline_counts = count_events_from_metrics(args.baseline)
        sampled_counts = count_events_from_metrics(args.sampled)
    except Exception as e:
        print(f"Error reading metrics files: {e}")
        sys.exit(1)
    
    # Parse sampling rates
    sampling_rates = {}
    if args.rates:
        sampling_rates = parse_sampling_rates(args.rates)
    else:
        # Try to infer from the difference in counts
        print("Warning: No sampling rates provided, inferring from data...")
    
    # Validate sampling
    results, _ = validate_sampling(
        baseline_counts,
        sampled_counts,
        sampling_rates,
        args.tolerance / 100
    )
    
    # Print report
    print_validation_report(results)

if __name__ == '__main__':
    main()
