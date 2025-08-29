N = 6
build:
	g++ client.cpp -i client.out
	g++ server.cpp -o server.out

run:
	echo "Not Implemented: Running a Single Iteration for client-server node"
.PHONY: plot
plot:
	jq '.k = "1000"' config.json > temp.json && mv temp.json config.json