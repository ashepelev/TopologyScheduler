__author__ = 'ash'

import time
import random
import time
import os
import sys

class TrafficGen:

    def __init__(self,node_list):
        self.node_list = node_list
        self.start = time.clock()
        self.traffic = dict()

    def generator(self):
        self.start = time.clock()
        while True:
            rand = random.randint(0,5)
            if rand == 0:
                capt_time = time.clock()
                if capt_time - self.start > 2: # refresh each 2 seconds
                    self.process_bandwidth(capt_time)
                    self.start = capt_time
                    self.traffic.clear()
                (src,dst) = self.example_load()
                if src == dst: # if src and dst are equal - we inc with mod
                    dst += 1
                    dst % len(self.node_list)
                length = random.randint(500,1500)
                pk = Packet(src,dst,length)
                if (src,dst) not in self.traffic:
                    self.traffic[(src,dst)] = 0
                self.traffic[(src,dst)] += length


    def process_bandwidth(self,capt_time):
        os.system('clear')
        for k in self.traffic.keys():
            bandwidth = self.traffic[k] / (capt_time - self.start)
            (src,dst) = k
            sys.stdout.write(str(src) + " > " + str(dst) + "\t\t" + str(bandwidth) + "\n")

    def example_load(self):
        """
        9 to 3 - heavy
        8 to 10 - heavy
        0 to * - low
        """
        nodelen = len(self.node_list)
        rand = random.randint(0,nodelen*3)
        if rand > 2*nodelen:
            (src,dst) = (9,3)
        elif rand <= 2*nodelen and rand >= nodelen:
            (src,dst) = (8,10)
        else:
            (src,dst) = (0,random.randint(0,nodelen-1))
        return (src,dst)

class Packet:

    def __init__(self, src, dst, length):
        self.src = src
        self.dst = dst
        self.len = length