N = 6
build:
	g++ client.cpp -i client.out
	g++ server.cpp -o server.out

run:
	echo "Not Implemented: Running a Single Iteration for client-server node"
.PHONY: plot
plot:
	@for i in $(shell seq 1 $(N)); do \
		sed -i 's/"k": "$((i-1))"/"k": "$((i))"/' config.json; \ 
	done

