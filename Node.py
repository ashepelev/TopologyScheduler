__author__ = 'ash'


class Node:

    def __init__(self, vid):
        self.id = vid
        self.neighbours = []

    def add_neighbours(self, n):
        self.neighbours.append(n)


class Switch(Node):

    def __init__(self, vid):
        self.id = vid
        self.neighbours = []

class Router(Node):

    ip_addr = ""

    def __init__(self,vid):
        self.id = vid
        self.neighbours = []

    def check_ip(ipa):
        octets = ipa.splite('.')
        if len(octets) != 4:
            print "IPv4 must have 4 octets"
            return False
        i = 0
        while i < len(octets):
            oc = int(octets[i])
            if oc < 0 or oc > 255:
                print "An octet must be in [0,255]"
                return False
            i+=1
        return True

    def assign_ip(self,ipa):  # to write the ip checker
        if check_ip(ipa):
            self.ip_addr = ipa

    def add_neighbours(self, n):
        if len(self.neighbours > 0)
            print "No more than 1 neighbours"
            return
        self.neighbours.append(n)


class Endpoint(Node):

    ip_addr = ""
    hostname = ""

    def __init__(self,vid):
        self.id = vid
        self.neighbours = []

    def assign_ip(self,ipa):
        self.ip_addr = ipa

    def assign_hostname(self, hn):
        self.hostname = hn

    def add_neighbours(self, n):
        if len(self.neighbours > 0)
            print("No more than 1 neighbours")
            return
        self.neighbours.append(n)

class ComputeNode(Endpoint):

    vcpu = 0
    ram = 0
    # should be an Openstack object with it's properties

    def assign_vcpu(self, vc):
        self.vcpu = vc

    def assign_ram(self,r):
        self.ram = r

class Storage(Endpoint):

    def __init__(self, vid):
        self.id = vid
        self.neighbours = []

class NetworkNode(Endpoint):

    def __init__(self, vid):
        self.id = vid
        self.neighbours = []

class CloudController(Endpoint):

    def __init__(self, vid):
        self.id = vid
        self.neighbours = []