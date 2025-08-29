N = 6
build:
	g++ client.c -o client
	g++ server.c -o server

run:
	echo "Not Implemented: Running a Single Iteration for client-server node"
.PHONY: plot
plot:
	jq '.k = "1000"' config.json > temp.json && mv temp.json config.json