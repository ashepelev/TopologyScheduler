__author__ = 'ash'

import Scheduler
import Edge

class BandwidthHistory:

    def __init__(self,node_list,edge_list):
        #self.hist = dict()
        sched = Scheduler.Scheduler(node_list, edge_list)
        self.route_matrix = sched.calc_routes()
        for x in edge_list: # initiate weights with default values
            x.init_weights()
        self.edge_dict = Edge.Edge.edges_list_to_dict(edge_list)


    def append(self,pair,value,bw_id):
        """
        Mapping the traffic data of the route to the edges (channels) of the route
        """
        (src,dst) = pair
        route = self.route_matrix[src][dst].route
        ei = Edge.EdgeInfo(value,bw_id)
        for i in range(0,len(route)-1): # iterate through route from src to dst
            (v1,v2) = (route[i],route[i+1])
            if self.edge_dict.has_key((v1,v2)): # cause we might keep them vice versa
                self.edge_dict[(v1,v2)].append_bandwidth(ei) # accumulate info on the edges
            else:
                self.edge_dict[(v2,v1)].append_bandwidth(ei)








