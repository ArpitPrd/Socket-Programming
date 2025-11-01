#!/usr/bin/env python3
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink

class WordCountTopo(Topo):
    def build(self, n):
        s1 = self.addSwitch('s1')
        
        for i in range(0, n+1):

            host = self.addHost(f"h{i}", ip=f"10.0.0.{i+1}/24")
            self.addLink(host, s1, cls=TCLink, bw=100)

def make_net(n):
    return Mininet(topo=WordCountTopo(n), controller=OVSController,
                   autoSetMacs=True, autoStaticArp=True, listenPort=5222)
