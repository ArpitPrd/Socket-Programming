# Makefile for Part 4: Round-Robin Scheduling

# Auto-detect if sudo is needed
ifneq ($(shell id -u), 0)
    SUDO = sudo
else
    SUDO =
endif

PYTHON = python3
CONFIG = config.json
PLOT_SCRIPT = runner.py



run-rr: 
	@echo "Running a single Round-Robin experiment on Mininet..."
	@$(SUDO) $(PYTHON) $(PLOT_SCRIPT) --single-run

plot: 
	@echo "Running experiments and generating comparison plot on Mininet..."
	@$(SUDO) $(PYTHON) $(PLOT_SCRIPT)


