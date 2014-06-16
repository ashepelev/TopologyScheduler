__author__ = 'ash'

import Scheduler
import Edge

class BandwidthHistory:

    def __init__(self,node_list,edge_list):
        self.hist = dict()
        sched = Scheduler.Scheduler(node_list, edge_list)
        self.route_matrix = sched.calc_routes()
        self.edge_dict = Edge.edges_list_to_dict(edge_list)


    def append(self,pair,value,time):
        (src,dst) = pair
        for i in range(0,len(self.route_matrix[src][dst])-1): # iterate through route from src to dst
            ei = Edge.EdgeInfo(value,time)
            self.edge_dict[(i,i+1)].append_bandwidth(ei) # accumulate info on the edges








