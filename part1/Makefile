K=5
P=0
build:
	g++ client.cpp -o client
	g++ server.cpp -o server

run:
	echo $P
	sudo K=$(K) P=$(P) python3 demo_runner.py

.PHONY: plot
plot:
	sudo python3 run_experiments.py
	python3 plot_results.py