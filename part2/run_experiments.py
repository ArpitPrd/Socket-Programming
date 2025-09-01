# STARTER CODE ONLY. EDIT AS DESIRED
#!/usr/bin/env python3
import re
import time
import csv
from pathlib import Path
from topo_wordcount import make_net
import json

# Config
K_VALUES = [1, 2, 5, 10, 20, 50, 100]#, 200, 400, 800]   
RUNS_PER_K = 5
SERVER_CMD = "./server --config config.json"
CLIENT_CMD_TMPL = "./client --config config.json"

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

def main():
    # Prepare CSV
    with RESULTS_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["k", "run", "elapsed_ms"])

    net = make_net()
    net.start()

    h_server = net.get("h1")

    # Ensure words.txt exists (shared FS)
    if not Path("words.txt").exists():
        Path("words.txt").write_text("cat,bat,cat,dog,dog,emu,emu,emu,ant\n")


    try:
        for k in K_VALUES:
            for r in range(1, RUNS_PER_K + 1):

                print(f"k={k},r={r}")
                modify_config("k", k) # should implement this function
                
                # Start server
                srv = h2.popen(SERVER_CMD, shell=True)
                time.sleep(0.5)  # give it a moment to bind                

                cmd = CLIENT_CMD_TMPL
                # this is just command line stuff, executes and closes
                out = h1.cmd(cmd)
                
                # parse ELAPSED_MS
                m = re.search(r"ELAPSED_MS:(\d+)", out)
                if not m:
                    print(f"[warn] No ELAPSED_MS found for k={k} run={r}. Raw:\n{out}")
                    continue
                ms = int(m.group(1))
                with RESULTS_CSV.open("a", newline="") as f:
                    csv.writer(f).writerow([k, r, ms])
                print(f"k={k} run={r} elapsed_ms={ms}")
                print(out)
                srv.terminate()
                time.sleep(0.2)
    finally:
        srv.terminate()
        time.sleep(0.2)
        net.stop()

if __name__ == "__main__":
    main()
