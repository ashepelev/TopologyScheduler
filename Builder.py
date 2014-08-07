from nova.scheduler.weights.TopologyWeigher import Node

__author__ = 'ash'

from nova.scheduler.weights.TopologyWeigher.Node import Switch
from nova.scheduler.weights.TopologyWeigher.Node import Router
from nova.scheduler.weights.TopologyWeigher.Node import ComputeNode
from nova.scheduler.weights.TopologyWeigher.Node import CloudController

import sys


class Builder:

    nodes = []

    def __init__(self):
        """


        """

    def load_node(self,node):
        id = len(self.nodes)
        node = Node(id)
        self.nodes.append(node)

    def set_ip(self):
        sys.stdout.write("Enter ip: ")

    def dispatch_add_type(self,words_cmd):
        idn = len(self.nodes)
        if words_cmd[1] == "sw":
            node = Switch(idn)
        elif words_cmd[1] == "rt":
            node = Router(idn)
        elif words_cmd[1] == "cn":
            node = ComputeNode(idn)
        elif words_cmd[1] == "cc":
            node = CloudController(idn)
        else:
            print "Wrong node type"
            return
        self.nodes.append(node)

    def check_neighbours_list(self,str_neighbour,add_id):
        try:
            neighbor_id = int(str_neighbour)
        except ValueError:
            print "neigbour_id is not an integer"
            return False
        if neighbor_id >= len(self.nodes) or neighbor_id < 0:
            print "Wrong neighbour id. No nodes with such id in topology"
            return False
        if neighbor_id == add_id:
            print "Neighbour id and added id are the same"
            return False
        return True

    def dispatch_add_neighbours(self,words_cmd,add_id):
        i = 2
        while i < len(words_cmd):
            if self.check_neighbours_list(words_cmd[i]):
                self.nodes[add_id].add_neighbours_by_one(int(words_cmd[i]))
                i += 1

    def dispatch_add_to_other_nodes(self, words_cmd,add_id):
        i = 2
        while i < len(words_cmd):
            if self.check_neighbours_list(words_cmd[i],add_id):
                self.nodes[i].add_neighbours_by_one(len(self.nodes)-1)
                i += 1

    def dispatch_add(self, words_cmd):
        if len(words_cmd) < 3:
            print "Usage: add <node_type> <neighbour_list>"
            return
        else:
            self.dispatch_add_type(words_cmd)
            self.dispatch_add_neighbours(words_cmd,len(self.nodes))
            self.dispatch_add_to_other_nodes(words_cmd,len(self.nodes))


    def dispatch_cmd(self, str_cmd):
        words = str_cmd.split(' ')
        if words[0] == "add": # add <node_type> <neighbour_list>
            self.dispatch_add(words)


