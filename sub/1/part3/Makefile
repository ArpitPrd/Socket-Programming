# Makefile for Part 3: FCFS with Greedy Client

ifneq ($(shell id -u), 0)
    SUDO = sudo
else
    SUDO =
endif

PYTHON = python3 
CONFIG = config.json
PLOT_SCRIPT = runner.py



run-fcfs: 
	@echo "Running a single FCFS experiment on Mininet..."
	@$(SUDO) $(PYTHON) $(PLOT_SCRIPT) --single-run
	@echo "Single experiment complete. Check terminal for results."

plot: 
	@echo "Running experiments for varying c values and generating plot on Mininet..."
	@$(SUDO) $(PYTHON) $(PLOT_SCRIPT)
	@echo "Plot generated: p3_plot.png"

