## General Pointers:

- can work with branches
- gitignore, ignores files that have not been added yet
- Make files for large number of files in the programming env
- goal of makefile is to compile based on what has been changed only, reduces the amount of time
- docs for jq: https://jqlang.org/manual/ 
- if some experiment were repeated 100 times, then 95 values will lie in that confidence interval zone
- how to calculate 95% interval https://en.wikipedia.org/wiki/Confidence_interval 
- sudo apt-get update is a command ran for getting all the dependencies updates and doesnt really install anything, upgrade does this
- which command provides the path to a command
- X11 forwardsing problems: http://www.faqs.org/docs/Linux-HOWTO/XDMCP-HOWTO.html
- can run iperf on VM using -c <ip address> -t <time>
- potential place for finding the logs: /var/log/libvirt/qemu/<vm-name>.log
- you need the image of ubuntu 22 to use the same

- how to set up ssh in vs code
    - [1] click on >< thing on the bottom or Remote:SSH Configure
    - in the configs file:
        - Host prd-arpit (any name for the server)
        - Hostname ip addr
        - User prd
    - Use the ref [1] and start the ssh again
    - enter the login password
- using json
    ```
    import json

    f = open(...)
    # loading data
    data = json.load(f)
    ... # edit the data
    # saving data
    with open(..., 'w') as f:
        json.dump(data, f, indent=<optional>)
    ```
- use this for setting git user:
    - git config --global user.name "name"
    - git config --global user.email "email addr"

    check this by:
    - git config --list
- NAT = Netowrk Address Translotors
- 10.0.0.0 to 10.255.255.255 are private netowrks that are reserved and cannot be pinged. however mininet is isolated and hence can be pinged easily. The hosts in mininet can ping eachother even if they have this address.
- Proxy server to monitor traffic
- the iso of ubuntu are present at different location and can download from the nearest neighbour
- htons converts to host bytes in network style
- use exit(1) to sys.exit()
- memcpy for assigning chars
- "," is const char * literal
- need const char * and size_t

## Errors
- can check logs: journalctl -xe, dmesg | less (also a source) these are the kernel logs, /var/logs/syslogs general ubuntu logs.
- maybe the mininet configured all the ports, now things seem very nice
- or IP address used was wrong
- the above is for not being able to scp
- even client server socket is working good: https://stackoverflow.com/questions/17341076/mininet-cannot-find-required-executable-controller for more info
- authentication cookies are not lined up in the host and VM and hence not able to launch the server
    - sudo xauth add $(xauth list | tail -1) // use this for copying the cookie to the root user's xauth list
    - this issue is common when trying to open GUI apps
    - this is because the root does not inhereit the users X11 credentials
    - may have to re run this every time

    - add this code to ~/.bashrc
    ```
    if [ "$DISPLAY" != "" ]; then
        xauth add $(xauth list | tail -1) 2>/dev/null
    fi
    ```

    - there is another option of not working with mn as the root
- iperf may not be able to work because of the virtualization overhead
- mininet: getting results for iperfudp, but not tcp, mostly because of more security more time
    - iperf internally runs as:
        - h1 iperf -s h2
        - h2 iperf -c ip_h1 
    - reversing the h1 and h2 could help
    - sol run iperf as follows:
        - h1 iperf -s & // acts as server
        - h2 iperf -c h1 // acts as client 
- pass -v to run in debug mode
- run CLI commands on python with &
- fgets blocks input to be taken from the python script

- finding errors in the run():
    - worked with make net
    - check the print is actually correct by logging "check"
    - try & on the run function
    - 
    ```
    h1.cmd('gcc -o server server.c')
    h1.cmd('gcc -o client client.c')
    ```
    - this is not an error, because changed h1 to h2, since they share the same filesystem, they basically write also to the same filesystem
    - remember linux model is a filesystem
    - works with binary on the system

- somehow, sudo did not allow the env to realize there was pandas
- Counter({'cat': 228, 'dog': 228, 'emu': 76, 'ant': 76, 'fox': 76, 'cow': 75, 'cow\n': 1})

## Assignment 
- Leaan to write network applications specifically
- Client server comm over TCP sockets
- CLient downloads a list of files from the server and counts the word freq 

## File reading protocol:

- TCP connection to the sever (this is listening on a pre-defined IP address and port, from config.json file)
    - Established connections remain persitant unitl clinet

- At server:
    - local file for words.txt contains csv
    - client can send requests like:
        - p,k\n
        - p = offset the starting pos of the zero indexed
        - k = number of words to read

    - server message type
        - messaage + EOF (op)

## Mininet

- Topo is used to define the topology in the network which is tree shaped, infact the class structuring is also tree shaped
- mininet walkthrough: https://mininet.org/walkthrough/
- running VM on a virtual machine is beneficial, since it allows for isolation
- Lets create:
    - host
    - switches
    - links
    on a single machine for testing and prototyping 
- network emulation software allows a launch with switches host sdn controller in a single command
- sdn is software defined networking 
    ```
    *** Creating network
    *** Adding controller
    *** Adding hosts:
    h1 h2 
    *** Adding switches:
    s1 
    *** Adding links:
    (h1, s1) (h2, s1) 
    *** Configuring hosts
    h1 h2 // running on the same vm but makes the host in two different sockets
    *** Starting controller
    c0 // may be controls the circuit
    *** Starting 1 switches
    s1 ...
    *** Starting CLI:

    ```

- the two hosts are connected to the open flow kernel switch
- the kernel switch is connected the OpenFlow controller
- can build many more topologies 
- sdn network in a box and build

- dump: information on network setup
```
mininet>  dump
<Host h1: h1-eth0:10.0.0.1 pid=1310> 
<Host h2: h2-eth0:10.0.0.2 pid=1312> 
<OVSSwitch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None pid=1317> // ovs controller
<Controller c0: 127.0.0.1:6653 pid=1303> // ovs switch
```
- net: shows network link between devices
```
mininet> net
h1 h1-eth0:s1-eth1
h2 h2-eth0:s1-eth2
s1 lo:  s1-eth1:h1-eth0 s1-eth2:h2-eth0
c0
```
- these are virual ehternet pairs between hosts and switches
- h1 ping h2
    - fist packet
    - extra latency for sdn controller
    - after the first the flows are cached in the switch and hence the latency reduces
    - 

- listening to ping from h1 to h2: produces all the seq# etc (nice stuff)
- clear: sudo mn -c good practice to do this, clears the session aptly, clears zoombie processes, that might prevent making a new mn arch

- iperf: helps find TCP Bandwidth between hosts

- customisable bw and links, delays, etc..
    - sudo mn --link tc,bw=10,delay=10ms

- how to run the same code using the CLI
    - h1 gcc -o server server.c
    - h2 gcc -o client client.c
    - h1 ./server port_number
    - h2 ./client hostname port_number

    this is a convinient way to read the inputs

## Mininet Python API

- API docs: https://mininet.org/api/classmininet_1_1net_1_1Mininet.html#a95aa95c3c505d25f4d7d5bb6cee1b785
- get: getNodeByName - returns nodes with given name
- ipBase: base ip address for the hosts
- mininet.net.IP: return IP Address class
- addLink has cls = TCLink (dk)
- like how the "filesystem" was shared in the CLI, we have here also, run it with "&" this is compulsary (this is like the localhost thing, ig)
- you can make a net mininet.net.Mininet class first and then build the topology or you can build and pass a variable with the topology

- workflow:
    - net = make_net()
    - net.start
    - h1, h2 = net.h1, net.h2
    - h1.cmd()
    - h2.cmd()

- mn emulates link bandwidth with HTB = Hierarchichal Token Bucket
    - Error: Warning: sch_htb: quantum of class 50001 is big. Consider r2q change
    - this is just a kernel warning (ignoer)
    - prints when the quantum of message being sent is too large compared to the intended bw
    - class can send a lot more data than it is intended rate before rescheduling
    - r2q parameter controls the rate to quentum how the rate is divided into quanta
- use popen (opens a pipe to and from the command line) the return object is a open file object that is connected to the pipe, this helps in reading and writing options
- this allows to write down the commands in the host h1 and execute them 
- basically mininet starts separate processes for each of the host, provides them with their own namespaces and the processes communicate amongst eachother and its own file descriptior for socketrs (makes host very light weight)
- virtual ethernet pairs are connected cables: basically interprocess communicattions are happening here
- all this is reused from the linux kernel softwares (the kernel switches) (using open vswitch)
- OVS can run in user space, kernel space support OpenFlow for control 
- run the real SDN controllers that are inherently present on the linux subsystem (dk)
- start chosen SDN controller pr connect to an external one
- connects to OVS with OpenFlow (dk)
- linux traddic control tc and htb/qdisc to emulate:
    - BW, Delay, Packet Loss, Queues (dk)
- working

## Finding 95 percentile

- a, b, c, d, e = X, S
    - then range = (X - eS/sqrt(5), X + eS/sqrt(5))

- find more references in this: https://en.wikipedia.org/wiki/Confidence_interval 
- the proportion of recomputes would tend towards 95 percent of the times

## Plan to go about the assignment

- use the virtual machine this way:
    - ssh prd@<ip address>
    - scp -r localdir prd@id_address
    - start working there
    - after having some running code come back and paste here
- Make the code in this machine itself, for saftety ofcourse

## Socket Programming

- socket can be thought of as aa memory buffer, write and read throught this buffer on wither side. except this is possoible across computers
- 
- The client needs to know the address of the server and the server may not know the address of the client
- Steps for creating socket on the client side:
    - socket system call
    - connect the socket with address of the server using connect
    - use read and write system callees to send and recieve data
- steps for creating socket on the server side:
    - create a socket with socket() system call
        - returns a file descriptor that refers to the end points:https://man7.org/linux/man-pages/man2/socket.2.html
        - for a protocol and domain, there exists only one type of protocol, can pass 0 here.
    - bind socket to an address using bind calls, port of the host
    - listen to the connectinos
    - accept() connections from the client
    - send and recieve data

- Communication possible if only of the same socket type and same domain
- Domains:
    - Unix Domain AF_UNIX
    - Internet Domain (IP) AF_INET
- Port numbers are 16bit unsigned interger = 256 ports maintina port relations
- port >= 2000 generally availbale
- Socket Types:
    - Stream Sockests: TCP SOCK_STREAM
    - Datagram Sockets: UDP SOCK_DGRAM
- used in web browseers
- chat applications
- FTPs
- Distos


- <sys/types.h>: used in number of system calls
- <sys/socket.h>: definition structures needed for sockets
- <netinet/in.h> contains constants and structures needed for internet domain accessing
- more about perros: https://www.linuxhowtos.org/data/6/perror.txt
- fd store the values recieved by the socket system calls and accept system calls
    - creates three tables: std input, std output, stderr
- sockaddr_in is a wrapper to the socket addresses
    - sin_family = AF_INET

- gethostbyaddr requires a binary, not a string, use gethostbyname
- listen and accept are server side functions, cannot perform on the client side by any chance
    - as a client you can connect, send, recv, on client_socket_fd
- file descriptor is the index of the table maintained the kernel, this is maintained for each process, this is just the id of the socket
    - 0: stdin
    - 1: stdout
    - 2: stderr ./a.out 2> .txt flows the errors (because of the 2)
    - 3+: socket is open
        - 3: listening socket
        - 4: client 1 connection
        - 5: client 2  connetnio
        - ...
    - there is a socket process, spawns multiple spocets and then maintaines a table

- bind:: binds the socket to the address (a system call) binds to current host, and the port number it will listen on.
- listen(sockfd, quieuing limit)
- block until a client connects to a server, wakes up the processor when connection has been established by the client, 
    - all communication is to be done with this file descriptor
    - pointer to the address of the client on the other end of the pointer
    - size of this structure

- read blocks until there is something for it to read and until client has executed a write
    - reads the limit or what we got and gives the size of the number.

## Socket Programming Python

- bind(gethostbyname(), port), gethostbyname allows the socket to be visible by anybody outside in theworld
- '' = allows the machine to be reachable by any address the machine has
- each client socket is received from some client performing connect
- Two clients are free to chat and using some dynamically allocated ports which are recycled for the next convo
- for faster IPC: use localhost, takes a shortcut through many layers
- server's client socket and clients client socket are identical peering though
- flush to read it may be present in the buffer
- send and recv handle network buffers
- return when associated network buffer has been filled or received
- our resp to call it again and again until the mesage has been filled
- recv = 0 bytes closed or closing connection
    - connection broken and may wait ont he receive forever
    - messages fixed lenght or delimited
    - indiacte how long they are
    - 

## checks

- buffer size may be a bottleneck

## Task for the Assignment

- Implement a client server comm using TCP sockets.
- Working:
    - Server sends a file containing a list of words to the client
    - Client counts the word freq

- Protocol:
    - (assume common configs.json for both of them)
    - Server:
        - Server listening on pre-defined IP Address and Port (from configs.json)
        - Local File:
            - Name: words.txt
        - request for words:
            - recieves format:
                - p,k\n
            - sends:
                - wp,wp+1,wp+2,wp+3...,wmin(p+k, EOF),{EOF if EOF or p>EOF else ""}\n
            - handle:
                - insuff words
                - inval offsets
                - and more
                - make sure a compulsaory send

    - Client:
        - Client establishes TCP Connection with the server
        - sends: 
            - p,k\n
            - here p = offset starting pos, zero indexed
            - k = number of words to read
        - recieves:
            - wp,wp+1,wp+2,wp+3...,wmin(p+k, EOF),{EOF if EOF or p>EOF else ""}\n
            - close the TCP connections
            - print:
                ```
                wordp, freq
                wordp+1, freq
                .
                .
                .
                ```
    - Connections: Reamins established until client closes it
    
    
    - Plots:
        - in python
        - completion time vs k
            ```
            
            for each value of k:
                times = []
                for 5 times:
                    t = Time(perform download)
                    time.append(t)
                l, u = confidence_interval(times)

            plot average completion time + confience interval vs k
            ```
          
        - Tip: store k, avg completion time in csv
    - explain the observation

    - Report:
        - contrast socket api in c++ and python
    
## Submissions
    - part1:
        - client.cpp
        - server.cpp
        - Makefile

- code in C++ for client and socket
- c++17 can be used
- do not create .h files
- do not print anything at the client when we are greater than EOF 
- part2 all the clients are the same
- part 2, no multithreading required
    - server accepts client requests concurrently but proccesses them one at a time (arrival order)
    - https://piazza.com/class/mdh2cbzosfp6qh/post/54 for multi-threading discussions
- variable shell discussion: https://piazza.com/class/mdh2cbzosfp6qh/post/64
- ubuntu 22 gives good results

- run_experiments.py: This is for the analysis section of your assignment. Running simulation for different values of p and k. Generating the CSV and plot.

demo_runner.py: This is for one-time execution of client and server with specific values of p and k, which are taken from the command line. This will be used to test whether your code can handle all the cases. Important point to note here, in this file, you can see these two lines of code:

K = int(os.environ.get("K", "5"))
P = int(os.environ.get("P", "0"))

This means P and K values are being taken from the environment. So in your make file, for make run, your code should take these values from the command line and set them in the environment.

- check STOP in cpp codes because I have used it as a speacial token but may not be in general
- run 32

## File Structure

- Network Topology FIle:
    - Use this for analyis
    - contains 2 hosts, one switch 
- Runner.py
    - check for plotting with confidence times
    - has opened only one connection

- plot_results.py
    - use this for plotting with 95% confidence interval 

- configs.json
    - server IP
    - server port
    - k, p
    - filename
    - num_repetions

- Makefile:
    - make build:
        - server.out client.out
    
    - make run:
        - runs a single iteration of client and server
    
    - make plot:
        - runs for varying k, num_repetion number of time
        - generates p1_plot.png


## Part 3

- FCFS may become biased to greedy servers

- JFI index, indicating fairness vs number of back to back requests, here assumed k = 5, 

- FCFS: monopolize
- RR: can client still monopoize under certain situations?

- running 5 times necessary?



## Submission Changes

- change file name to pi_plot.png
- change p, k to receive the entire file

- contrast between api  
- multiplexing on TCP Ports