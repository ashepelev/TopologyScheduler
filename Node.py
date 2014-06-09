__author__ = 'ash'


class Node:

    def __init__(self, vid):
        self.id = vid

 #   def add_neighbours_by_one(self, n):
 #       self.neighbours.append(n)

 #   def set_neighbours(self, neigh_list):
 #      self.neighbours = neigh_list


class Switch(Node):

    def __init__(self, vid):
        self.id = vid

class Router(Node):

    def __init__(self,vid,hostn):
        self.id = vid
        self.hostname = hostn

    def check_ip(self, ipa):
        octets = ipa.split('.')
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
        if self.check_ip(ipa):
            self.ip_addr = ipa

  #  def add_neighbours(self, n):
  #      if len(self.neighbours > 0):
  #         print "No more than 1 neighbours"
  #          return
  #      self.neighbours.append(n)


class Endpoint(Node):

    ip_addr = ""
    hostname = ""

    def __init__(self,vid,hostn):
        self.id = vid
        self.hostname = hostn

    def assign_ip(self,ipa):
        self.ip_addr = ipa

    def assign_hostname(self, hn):
        self.hostname = hn

class ComputeNode(Endpoint):

    def assign_vcpu(self, vc):
        self.vcpu = vc

    def assign_ram(self,r):
        self.ram = r

class Storage(Endpoint):

   def __init__(self,vid,hostn):
        self.id = vid
        self.hostname = hostn

   def setLoad(self,load):
       self.load = load

class NetworkNode(Endpoint):
    def __init__(self,vid,hostn):
        self.id = vid
        self.hostname = hostn


class CloudController(Endpoint):

    def __init__(self,vid,hostn):
        self.id = vid
        self.hostname = hostn
