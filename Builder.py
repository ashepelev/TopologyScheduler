__author__ = 'ash'

import Node
from Node import Switch
from Node import Router
from Node import ComputeNode
from Node import CloudController

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
        elif words_cmd[1] == "cc"
            node = CloudController(idn)
        else:
            print "Wrong node type"
            return
        self.nodes.append(node)

    def dispatch_add(words_cmd):
        if len(words_cmd) != 4:
            print "Usage: add <node_type> <hostname> <neighbor>"
            return
        else:


    def dispatch_cmd(self, str_cmd):
        words = str_cmd.split(' ')
        if words[0] == "add": # add <node_type> <hostname> <neighbor>
            dispatch_add(words)


