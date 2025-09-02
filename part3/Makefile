# Makefile for Part 3: FCFS with Greedy Client

ifneq ($(shell id -u), 0)
    SUDO = sudo
else
    SUDO =
endif

PYTHON = python3
CONFIG = config.json
PLOT_SCRIPT = runner.py
OUTPUT_DIR = results_part3
REQUIREMENTS = requirements.txt

.PHONY: all clean run-fcfs plot setup install

all: setup

install: $(REQUIREMENTS)
	@echo "Installing python dependencies from $(REQUIREMENTS)..."
	@$(PYTHON) -m pip install -r $(REQUIREMENTS)
	@echo "Dependencies installed successfully."

setup:
	@echo "Setting up Part 3 environment..."
	@mkdir -p $(OUTPUT_DIR)
	@mkdir -p logs
	@if [ ! -f words.txt ]; then \
		echo "Creating sample words.txt file..."; \
		$(PYTHON) -c "words = ['apple', 'banana', 'cat', 'dog', 'elephant', 'fox', 'grape', 'horse', 'ice', 'jacket'] * 50; \
		with open('words.txt', 'w') as f: f.write(','.join(words))"; \
	fi
	@if [ ! -f $(CONFIG) ]; then \
		echo "Creating default config.json..."; \
		echo '{"server_ip": "10.0.0.100", "server_port": 8887, "filename": "words.txt", "num_clients": 10, "c": 1, "p": 0, "k": 5}' > $(CONFIG); \
	fi

run-fcfs: setup
	@echo "Running a single FCFS experiment on Mininet..."
	@$(SUDO) $(PYTHON) $(PLOT_SCRIPT) --single-run
	@echo "Single experiment complete. Check terminal for results."

plot: setup
	@echo "Running experiments for varying c values and generating plot on Mininet..."
	@$(SUDO) $(PYTHON) $(PLOT_SCRIPT)
	@echo "Plot generated: p3_plot.png"

clean:
	@echo "Cleaning up..."
	@rm -rf $(OUTPUT_DIR) logs __pycache__
	@rm -f p3_plot.png
	@$(SUDO) pkill -f "python3 server.py" 2>/dev/null || true
	@$(SUDO) mn -c 2>/dev/null || true
	@echo "Cleanup complete."