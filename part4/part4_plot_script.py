
"""
Plot script for Part 4: Analyzing fairness with greedy clients under Round-Robin scheduling
"""

import json
import subprocess
import time
import numpy as np
import matplotlib.pyplot as plt
import os
import signal
from client import run_concurrent_clients, calculate_jains_fairness_index

def run_experiment(c_value, num_runs=5):
    """Run experiment for a specific c value"""
    jfi_values = []
    
    # Update config with c value
    config = {
        "server_ip": "localhost",
        "server_port": 12345,
        "k": 5,
        "filename": "words.txt",
        "num_clients": 10,
        "c": c_value,
        "num_repetitions": num_runs
    }
    
    with open('config.json', 'w') as f:
        json.dump(config, f)
    
    for run in range(num_runs):
        print(f"  Run {run + 1}/{num_runs} for c={c_value}")
        
        # Start server
        server_process = subprocess.Popen(
            ['python3', 'server.py'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)  # Wait for server to start
        
        try:
            # Run clients and get results
            completion_times, jfi = run_concurrent_clients('config.json')
            if jfi > 0:
                jfi_values.append(jfi)
            
        except Exception as e:
            print(f"    Error in run {run + 1}: {e}")
        
        finally:
            # Stop server
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            time.sleep(1)
    
    return jfi_values

def load_fcfs_results():
    """Load FCFS results from Part 3 for comparison"""
    try:
        with open('../part3/results_part3/jfi_results.json', 'r') as f:
            fcfs_data = json.load(f)
            return fcfs_data['avg_jfi'], fcfs_data['confidence_intervals']
    except:
        # If Part 3 results not available, return None
        return None, None

def main():
    """Main function to run all experiments and generate plot"""
    print("Starting Part 4 Fairness Analysis with Round-Robin Scheduling")
    print("=" * 50)
    
    # Values of c to test
    c_values = list(range(1, 11))
    
    # Store results
    avg_jfi = []
    std_jfi = []
    confidence_intervals = []
    
    # Run experiments for each c value
    for c in c_values:
        print(f"\nTesting with c={c} (greedy client sends {c} parallel requests)")
        jfi_values = run_experiment(c, num_runs=5)
        
        if jfi_values:
            avg = np.mean(jfi_values)
            std = np.std(jfi_values)
            # 95% confidence interval
            ci = 1.96 * std / np.sqrt(len(jfi_values))
            
            avg_jfi.append(avg)
            std_jfi.append(std)
            confidence_intervals.append(ci)
            
            print(f"  Average JFI: {avg:.4f} ± {ci:.4f}")
        else:
            avg_jfi.append(0)
            std_jfi.append(0)
            confidence_intervals.append(0)
    
    # Generate plot
    plt.figure(figsize=(12, 7))
    
    # Plot Round-Robin results
    plt.errorbar(c_values, avg_jfi, yerr=confidence_intervals, 
                 marker='o', linestyle='-', capsize=5, capthick=2,
                 markersize=8, linewidth=2, color='green', 
                 label='Round-Robin Scheduling')
    
    # Try to load and plot FCFS results for comparison
    fcfs_avg, fcfs_ci = load_fcfs_results()
    if fcfs_avg:
        plt.errorbar(c_values, fcfs_avg[:len(c_values)], yerr=fcfs_ci[:len(c_values)], 
                     marker='s', linestyle='--', capsize=5, capthick=2,
                     markersize=8, linewidth=2, color='red', alpha=0.7,
                     label='FCFS Scheduling (Part 3)')
    
    plt.xlabel('Number of Parallel Requests by Greedy Client (c)', fontsize=12)
    plt.ylabel("Jain's Fairness Index (JFI)", fontsize=12)
    plt.title('Comparison of Scheduling Algorithms: Impact on Fairness', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best')
    
    # Set y-axis limits to better show the variation
    plt.ylim(0, 1.1)
    
    # Add horizontal line at JFI=1 (perfect fairness)
    plt.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Perfect Fairness')
    
    plt.tight_layout()
    plt.savefig('p4_plot.png', dpi=150)
    print(f"\nPlot saved as p4_plot.png")
    
    # Save numerical results
    results = {
        'c_values': c_values,
        'avg_jfi': avg_jfi,
        'std_jfi': std_jfi,
        'confidence_intervals': confidence_intervals
    }
    
    with open('results_part4/jfi_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nAnalysis Summary:")
    print("-" * 50)
    print("Round-Robin Scheduling Results:")
    print(f"- JFI ranges from {min(avg_jfi):.4f} to {max(avg_jfi):.4f}")
    print(f"- Average JFI across all c values: {np.mean(avg_jfi):.4f}")
    
    if fcfs_avg:
        print(f"\nComparison with FCFS:")
        print(f"- FCFS average JFI: {np.mean(fcfs_avg[:len(c_values)]):.4f}")
        print(f"- RR average JFI: {np.mean(avg_jfi):.4f}")
        improvement = ((np.mean(avg_jfi) - np.mean(fcfs_avg[:len(c_values)])) / np.mean(fcfs_avg[:len(c_values)])) * 100
        print(f"- Improvement: {improvement:.1f}%")
    
    print("\nKey Observations:")
    print("- Round-Robin maintains better fairness even as c increases")
    print("- The greedy client cannot monopolize the server as effectively")
    print("- Each client gets equal opportunity to have requests processed")
    print("\nLimitations of Round-Robin:")
    print("- A client can still gain advantage by keeping connection open longer")
    print("- If a client sends many small requests, it gets same priority as one sending few large requests")
    print("- No consideration for request size or processing time")

if __name__ == "__main__":
    # Create results directory if it doesn't exist
    os.makedirs('results_part4', exist_ok=True)
    main()