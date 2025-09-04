# Makefile for Part 3: FCFS with Greedy Client

ifneq ($(shell id -u), 0)
    SUDO = sudo
else
    SUDO =
endif

PYTHON = /home/prd/COL334/myenv/bin/python3
CONFIG = config.json
PLOT_SCRIPT = runner.py



run-fcfs: 
	sudo /home/prd/COL334/myenv/bin/python3 runner.py --single-run

plot: 
	@echo "Running experiments for varying c values and generating plot on Mininet..."
	@$(SUDO) $(PYTHON) $(PLOT_SCRIPT)
	@echo "Plot generated: p3_plot.png"

