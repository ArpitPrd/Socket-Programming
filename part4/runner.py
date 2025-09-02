#!/usr/bin/env python3
import json
import os
import time
import glob
import numpy as np
import matplotlib.pyplot as plt
import sys
import argparse
from mininet.cli import CLI
from topology import create_network

class Runner:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        

        self.server_ip = self.config['server_ip']
        self.port = self.config['server_port']
        self.num_clients = self.config['num_clients']
        self.c = self.config['c']  # Batch size for rogue client
        self.p = self.config['p']  # Offset (always 0) since we want to download the full file
        self.k = self.config['k']  # Words per request (always 5)
        
        print(f"Config: {self.num_clients} clients, c={self.c}, p={self.p}, k={self.k}")

        os.makedirs('results_part4', exist_ok=True)
        #print(f"Config: {self.num_clients} clients, c={self.c}")

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
        if not values or len(values) == 0:
            return 0
        # JFI uses throughput (inverse of completion time)
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

    # def run_experiment(self, c_value):
    #     print(f"Running experiment with c={c_value} on Mininet...")
    #     self.cleanup_logs()
        
    #     net = create_network(num_clients=self.num_clients)
        
    #     # Start server and clients using Mininet CLI for stability
    #     cmd_file_path = 'run_commands.txt'
    #     with open(cmd_file_path, 'w') as f:
    #         f.write('server python3 server.py &\n')
    #         f.write('py time.sleep(3)\n')
    #         f.write(f'client1 python3 client.py --batch-size {c_value} --client-id rogue &\n')
    #         for i in range(2, self.num_clients + 1):
    #             f.write(f'client{i} python3 client.py --batch-size 1 --client-id normal_{i} &\n')
    #         # Wait for all background jobs to finish. A simple long sleep is sufficient here.
    #         f.write('py time.sleep(15)\n')
    #         f.write('exit\n')

    #     CLI(net, script=cmd_file_path)
    #     net.stop()
    #     os.remove(cmd_file_path)
        
    #     return self.parse_logs()


    def run_experiment(self, c_value):
        """Run single experiment with given c value"""
        print(f"Running experiment with c={c_value}")
        
        # Clean logs
        self.cleanup_logs()
        
        # Create network
        from topology import create_network
        net = create_network(num_clients=self.num_clients)
        
        try:
            # Get hosts
            server = net.get('server')
            clients = [net.get(f'client{i+1}') for i in range(self.num_clients)]
            
            # Start server (students create server.py)
            print("Starting server...")
            server_proc = server.popen("python3 server.py")
            time.sleep(3)
            
            # Start clients
            print("Starting clients...")
            # Client 1 is rogue (batch size c)
            rogue_proc = clients[0].popen(f"python3 client.py --batch-size {c_value} --client-id rogue")
            
            # Clients 2-N are normal (batch size 1)
            normal_procs = []
            for i in range(1, self.num_clients):
                proc = clients[i].popen(f"python3 client.py --batch-size 1 --client-id normal_{i+1}")
                normal_procs.append(proc)
            
            # Wait for all clients
            rogue_proc.wait()
            for proc in normal_procs:
                proc.wait()
            
            # Stop server
            server_proc.terminate()
            server_proc.wait()
            time.sleep(2)
            
            # Parse results
            time.sleep(1)
            results = self.parse_logs()
            
            return results
            
        finally:
            net.stop()


    def run_varying_c(self):
        c_values = list(range(1, 11))
        jfi_results = []
        for c in c_values:
            print(f"\n--- Testing c = {c} ---")
            # Running once is sufficient for the plot, but multiple runs would be better for confidence
            completion_times = self.run_experiment(c)
            if completion_times:
                jfi = self.calculate_jfi(completion_times)
                jfi_results.append(jfi)
                print(f"Experiment with c={c} completed. JFI: {jfi:.4f}")
            else:
                jfi_results.append(0)
        
        # Save results for plotting
        results_data = {'c_values': c_values, 'avg_jfi': jfi_results}
        with open('results_part4/jfi_results.json', 'w') as f:
            json.dump(results_data, f, indent=2)

        print("\nAll experiments completed")
        self.plot_jfi_vs_c(results_data)

    def plot_jfi_vs_c(self, rr_results):
        c_values = rr_results['c_values']
        rr_jfi = rr_results['avg_jfi']

        plt.figure(figsize=(10, 6))
        
        # Plot Round-Robin
        plt.plot(c_values, rr_jfi, marker='o', linestyle='-', color='green', label='Round-Robin Scheduling')

        # Load and plot FCFS data from Part 3 for comparison
        try:
            with open('../part3/results_part4/jfi_results.json', 'r') as f:
                fcfs_results = json.load(f)
                plt.plot(c_values, fcfs_results['avg_jfi'], marker='s', linestyle='--', color='red', label='FCFS Scheduling (from Part 3)')
        except FileNotFoundError:
            print("Could not find Part 3 results for comparison plot.")

        plt.xlabel('Number of Parallel Requests by Greedy Client (c)')
        plt.ylabel("Jain's Fairness Index (JFI)")
        plt.title('Fairness Comparison: Round-Robin vs. FCFS')
        plt.grid(True, alpha=0.3)
        plt.xticks(c_values)
        plt.ylim(0.7, 1.1)
        plt.axhline(y=1.0, color='grey', linestyle='--', label='Perfect Fairness')
        plt.legend()
        
        plot_filename = 'p4_plot.png'
        plt.savefig(plot_filename)
        print(f"\nPlot saved as {plot_filename}")

def main():
    parser = argparse.ArgumentParser(description="Run Round-Robin fairness experiments.")
    parser.add_argument('--single-run', action='store_true', help='Run a single experiment')
    args = parser.parse_args()
    
    runner = Runner()
    if args.single_run:
        completion_times = runner.run_experiment(runner.c)
        if completion_times:
            jfi = runner.calculate_jfi(completion_times)
            print("\n=== Single Run Results ===")
            print(f"Jain's Fairness Index: {jfi:.4f}")
    else:
        runner.run_varying_c()

if __name__ == '__main__':
    if os.geteuid() != 0:
        print("This script uses Mininet and must be run with sudo.")
        sys.exit(1)
    main()