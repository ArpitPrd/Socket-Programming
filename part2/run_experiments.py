# STARTER CODE ONLY. EDIT AS DESIRED
#!/usr/bin/env python3
import re
import time
import csv
from pathlib import Path
from topo_wordcount import make_net
import json

# Config
K_VALUE = 20
RUNS_PER_K = 5
SERVER_CMD = "python3 server.py --config config.json"

RESULTS_CSV = Path("results.csv")

def modify_config(
        key:str, 
        value:any,
        config_filename="config.json", 
    ) -> None:
    """
    changes this particular key with the corresponding value, if not present then adds this key to the file
    """
    json_file = open(config_filename, 'r')
    data = json.load(json_file)
    data[key] = value
    data["server_port"] += 1
    json_file.close()

    with open(config_filename, 'w') as f:
        json.dump(data, f)
    
    return

def read_json(filename="config.json") -> dict:
    with open(filename) as f:
        data = json.load(f)  
    return data

def end_server(srv):
    srv.terminate()
    time.sleep(0.2)
    return

def elaspsed_ms(out):
    m = re.search(r"ELAPSED_MS:(\d+)", out)
    if not m:
        print(f"[warn] No ELAPSED_MS found. Raw:\n{out}")
        return -1
    return int(m.group(1))

def main():
    data = read_json()
    NUM_CLIENTS = data["num_clients"]

    # Prepare CSV
    with RESULTS_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["nc", "r", "elapsed_ms"])

    net = make_net()
    net.start()

    h_server = net.get("h0")
    

    clients = [net.get(f"h{i}") for i in range(1, NUM_CLIENTS+1)]

    # Ensure words.txt exists (shared FS)
    if not Path("words.txt").exists():
        Path("words.txt").write_text("cat,bat,cat,dog,dog,emu,emu,emu,ant\n")


    try:
        for nc in NUM_CLIENTS:
            
            modify_config("num_clients", nc)
            
            for r in range(1, RUNS_PER_K + 1):
                # Start server
                srv = h_server.popen(SERVER_CMD, shell=True)
                time.sleep(0.5)

                clients = [net.get(f"h{i}") for i in range(1, nc+1)]
                procs = [h.popen("python3 client.py") for h in clients]
                
                outs = [p.communicate()[0].decode() for p in procs]

                elaspsed_mss_list = [elaspsed_ms(out) for out in outs]

                end_server(srv)
                
                
                avg_compl_per_client_ms = sum(elaspsed_mss_list) / len(elaspsed_mss_list)


                print(f"[info] n_clients={nc}, run={r}, avg_compl_time_per_person={avg_compl_per_client_ms}")
                with RESULTS_CSV.open("a", newline="") as f:
                    w = csv.writer(f)
                    w.writerow([nc, r, avg_compl_per_client_ms])
    finally:
        end_server(srv) 
        net.stop()

if __name__ == "__main__":
    main()