__author__ = 'ash'

class Edge:

    def __init__(self,node_pair,maxb):
        self.node_pair = node_pair
        self.maxb = maxb

    def assign_avg_bandw(self,ab):
        self.avg_bandw = ab

