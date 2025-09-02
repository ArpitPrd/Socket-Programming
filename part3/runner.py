#!/usr/bin/env python3
import json
import os
import time
import glob
import numpy as np
import subprocess
import matplotlib.pyplot as plt
import sys
import argparse
from mininet.cli import CLI
from topology import create_network

class Runner:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.num_clients = self.config.get('num_clients', 10)
        self.c = self.config.get('c', 1)
        print(f"Config: {self.num_clients} clients, c={self.c}")

    def cleanup_logs(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')
        for log in glob.glob("logs/*.log"):
            os.remove(log)
        print("Cleaned old logs")

    def parse_logs(self):
        completion_times = []
        log_files = glob.glob("logs/*.log")
        if len(log_files) < self.num_clients:
            print(f"Warning: Expected {self.num_clients} log files, but found {len(log_files)}")
            return []
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    completion_times.append(float(f.read().strip()))
            except (IOError, ValueError):
                pass
        return completion_times

    def calculate_jfi(self, values):
        if not values or len(values) < 2:
            return 1.0
        throughputs = [1.0 / v for v in values if v > 0]
        if not throughputs:
            return 0
        n = len(throughputs)
        sum_throughputs = sum(throughputs)
        sum_squares = sum(t**2 for t in throughputs)
        if sum_squares == 0:
            return 0
        jfi = (sum_throughputs ** 2) / (n * sum_squares)
        return jfi

    def run_experiment(self, c_value):
        print(f"Running experiment with c={c_value} on Mininet...")
        self.cleanup_logs()
        
        net = create_network(num_clients=self.num_clients)
        
        # Create a command script for Mininet CLI
        cmd_file_path = 'run_commands.txt'
        with open(cmd_file_path, 'w') as f:
            f.write('server python3 server.py &\n')
            f.write('py time.sleep(3)\n') # Give server time to start
            # Start clients, rogue first, then normal ones
            f.write(f'client1 python3 client.py --batch-size {c_value} --client-id rogue &\n')
            for i in range(2, self.num_clients + 1):
                f.write(f'client{i} python3 client.py --batch-size 1 --client-id normal_{i} &\n')
            f.write('py print("Waiting for clients to finish...")\n')
            f.write('py time.sleep(20)\n') # Generous wait time for clients
            f.write('py print("Clients should be finished. Exiting.")\n')
            f.write('exit\n')

        print("Starting Mininet CLI and executing commands...")
        CLI(net, script=cmd_file_path)

        print("Mininet script finished. Stopping network...")
        net.stop()
        os.remove(cmd_file_path)
        
        completion_times = self.parse_logs()
        return completion_times

    def run_varying_c(self):
        c_values = list(range(1, 11))
        jfi_results = {}
        for c in c_values:
            print(f"\n--- Testing c = {c} ---")
            completion_times = self.run_experiment(c)
            if completion_times:
                jfi = self.calculate_jfi(completion_times)
                jfi_results[c] = jfi
                print(f"Experiment with c={c} completed. JFI: {jfi:.4f}")
            else:
                jfi_results[c] = 0
                print(f"Experiment with c={c} failed.")
        print("\nAll experiments completed")
        self.plot_jfi_vs_c(jfi_results)

    def plot_jfi_vs_c(self, results):
        if not results:
            print("No results to plot.")
            return
        c_values = sorted(results.keys())
        jfi_values = [results[c] for c in c_values]
        plt.figure(figsize=(10, 6))
        plt.plot(c_values, jfi_values, marker='o', linestyle='-', color='b', label='FCFS Scheduling')
        plt.xlabel('Number of Parallel Requests by Greedy Client (c)')
        plt.ylabel("Jain's Fairness Index (JFI)")
        plt.title('Impact of Greedy Client on Fairness under FCFS Scheduling')
        plt.grid(True, alpha=0.3)
        plt.xticks(c_values)
        plt.ylim(0, 1.1)
        plt.axhline(y=1.0, color='g', linestyle='--', label='Perfect Fairness (JFI=1.0)')
        plt.legend()
        plot_filename = 'p3_plot.png'
        plt.savefig(plot_filename)
        print(f"\nPlot saved as {plot_filename}")

def main():
    parser = argparse.ArgumentParser(description="Run FCFS fairness experiments on Mininet.")
    parser.add_argument('--single-run', action='store_true', help='Run a single experiment with c from config.json')
    args = parser.parse_args()
    runner = Runner()
    if args.single_run:
        completion_times = runner.run_experiment(runner.c)
        if completion_times:
            jfi = runner.calculate_jfi(completion_times)
            print("\n=== Single Run Results ===")
            print(f"Completion Times (s): {completion_times}")
            print(f"Jain's Fairness Index: {jfi:.4f}")
        else:
            print("Single run failed to produce results.")
    else:
        runner.run_varying_c()

if __name__ == '__main__':
    if os.geteuid() != 0:
        print("This script uses Mininet and must be run with sudo.")
        sys.exit(1)
    main()