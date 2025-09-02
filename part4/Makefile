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
REQUIREMENTS = requirements.txt

.PHONY: all clean run-rr plot setup install

# Default target
all: setup

# Installs required python packages
install:
	@echo "Installing python dependencies..."
	@pip install numpy matplotlib

# Sets up the environment
setup:
	@echo "Setting up Part 4 environment..."
	@mkdir -p results_part4 logs
	@if [ ! -f words.txt ]; then \
		echo "Creating sample words.txt file..."; \
		$(PYTHON) -c "import random; words = ['apple', 'banana', 'cat', 'dog', 'elephant'] * 40; random.shuffle(words); \
		with open('words.txt', 'w') as f: f.write(','.join(words))"; \
	fi
	@if [ ! -f $(CONFIG) ]; then \
		echo "Creating default config.json..."; \
		echo '{"server_ip": "10.0.0.100", "server_port": 8887, "filename": "words.txt", "num_clients": 10, "c": 1, "k": 5}' > $(CONFIG); \
	fi

# Runs a single experiment on Mininet [cite: 125]
run-rr: setup
	@echo "Running a single Round-Robin experiment on Mininet..."
	@$(SUDO) $(PYTHON) $(PLOT_SCRIPT) --single-run

# Runs the full experiment suite and generates the plot [cite: 126]
plot: setup
	@echo "Running experiments and generating comparison plot on Mininet..."
	@$(SUDO) $(PYTHON) $(PLOT_SCRIPT)

# Cleans up generated files
clean:
	@echo "Cleaning up..."
	@rm -rf results_part4 logs __pycache__
	@rm -f p4_plot.png *.pyc run_commands.txt
	@$(SUDO) pkill -f "python3 server.py" 2>/dev_null || true
	@$(SUDO) mn -c 2>/dev/null || true