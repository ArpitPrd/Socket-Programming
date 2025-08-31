build:
	g++ client.cpp -o client
	g++ server.cpp -o server

run:
	sudo python3 demo_runner.py
.PHONY: plot
plot:
	sudo python3 run_experiment.py
	sudo plot_results.py