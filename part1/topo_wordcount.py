#!/usr/bin/env python3
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink
import json

class WordCountTopo(Topo):
    def build(self):
        with open("config.json") as f:
            data = json.load(f)
        ip = data["server_ip"]
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip=ip)
        self.addLink(h1, s1, cls=TCLink, bw=100)
        self.addLink(h2, s1, cls=TCLink, bw=100)

def make_net():
    return Mininet(topo=WordCountTopo(), controller=OVSController,
                   autoSetMacs=True, autoStaticArp=True, listenPort=5222)
