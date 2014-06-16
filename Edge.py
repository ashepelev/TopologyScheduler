__author__ = 'ash'

from collections import deque

class Edge:

    def __init__(self,node_pair,maxb):
        self.node_pair = node_pair
        self.maxb = maxb
        self.bandhist = deque()
        self.histtime = 3600 # keep history for one hour
        self.hist_growed = False

    def assign_avg_bandw(self,ab):
        self.avg_bandw = ab

    def append_bandwidth(self,edgeinfo):
        self.bandhist.append(edgeinfo)
        if not self.hist_growed:
            if self.bandhist[len(self.bandhist)-1].time - self.bandhist[0] > self.histtime:
                self.hist_growed = True
                self.bandhist.popleft()
        else:
            self.bandhist.popleft()

    @staticmethod
    def edges_list_to_dict(edge_list):
        res = dict()
        for edge in edge_list:
            res[(edge.node_pair[0]),(edge.node_pair[1])] = edge
        return res

class EdgeInfo:

    def __init__(self,value,time):
        self.value = value
        self.time = time