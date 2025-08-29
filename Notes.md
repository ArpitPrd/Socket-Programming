## General Pointers:

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

## File Structure

- Network Topology FIle:
    - Use this for analyis
    - contains 2 hosts, one switch 
- Runner.py
    - check for plotting with confidence times
    - 

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