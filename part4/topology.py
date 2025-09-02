#!/usr/bin/env python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

# Default number of clients
DEFAULT_CLIENTS = 10
# =============================================================================

class SimpleTopo(Topo):
    def __init__(self, num_clients=DEFAULT_CLIENTS):
        Topo.__init__(self)
        
        # Create switch
        switch = self.addSwitch('s1', cls=OVSSwitch)
        
        # Create server
        server = self.addHost('server', ip='10.0.0.100')
        
        # Create clients
        clients = []
        for i in range(num_clients):
            client = self.addHost(f'client{i+1}', ip=f'10.0.0.{i+1}')
            clients.append(client)
        
        # Connect server to switch with hardcoded bandwidth=1
        self.addLink(server, switch, bw=1)
        
        # Connect all clients to switch with hardcoded bandwidth=1
        for client in clients:
            self.addLink(client, switch, bw=1)

def create_network(num_clients=DEFAULT_CLIENTS):
    """Create and start the network with hardcoded bandwidth=1 for all links"""
    topo = SimpleTopo(num_clients)
    net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink)
    net.start()
    return net

if __name__ == '__main__':
    # This block is for running the script directly to get a Mininet CLI.
    setLogLevel('info')
    
    print(f"Creating network with {DEFAULT_CLIENTS} clients...")
    net = create_network()
    
    print("\nNetwork created successfully! Mininet CLI is ready.")
    print("Use 'xterm server client1' to open terminals for the hosts.")
    
    # Start the Mininet command-line interface
    CLI(net)
    
    # This will run when you exit the CLI
    print("Stopping network...")
    net.stop()