from nova.scheduler.weights.TopologyWeigher import Node

__author__ = 'ash'

from sets import Set
import sys
#import pulp

class Task:

    def __init__(self,vm_dep_list,storage_priority,public_priority):
        self.vm_dep_list = vm_dep_list
        self.storage_priority = storage_priority
        self.public_priority = public_priority

    @staticmethod
    def example_task():
        vm_dep_list = [(2,20)] # list of dependencies. format: (<compute_node_id>,<priority>)
        #storage_priority = 4
        #public_priority = 4
        task = Task(vm_dep_list,1,1)
        return task

class Scheduler:

    def __init__(self,node_list,edges_list):
        self.node_list = node_list
        self.edge_list = edges_list
        self.dim = len(node_list)
        self.infinity = 10000
        self.undefined = -1

    def make_adjacency_matrix(self):
     #   matrix = np.matrix(np.zeros((self.dim,self.dim),dtype=np.int))
        matrix = [[self.infinity for x in xrange(self.dim)] for y in xrange(self.dim)]
     #   test = matrix[0][1]
        for edge in self.edge_list:
            i,j = edge.node_pair
            test = matrix[i][j]
            matrix[i][j] = int(1)
            matrix[j][i] = int(1)
        return matrix

    def min_distance(self,dist,q):
        """
        Finds in dist minimal distance with indexes from the queue q
        """
        min = sys.maxint
        minind = -1
        for elem in q:
            if (dist[elem] < min):
                min = dist[elem]
                minind = elem
        return minind

    def dijkstra(self,matrix,src):
        """
        Standard Dijkstra algorithm. For source finds shortest pathes to every other node.
        """
        dist = [self.infinity for x in xrange(self.dim)]
        previous = [self.undefined for x in xrange(self.dim)]
        route_list = [[] for x in xrange(self.dim)]
        dist[src] = 0
    #    previous[src] = src
        q = Set()
        for i in range(0,self.dim):
            q.add(i)
        while (len(q) > 0):
            if (len(q) == self.dim):
                u = src
            else:
                u = self.min_distance(dist,q)
            q.remove(u)

            target = u
            path_node = u
            while previous[path_node] != self.undefined:
                route_list[target].append(path_node)
                path_node = previous[path_node]
            route_list[target].append(src)
            route_list[target].reverse() # as we aggregate it reverse

            for j in range(0,self.dim):
                if j == u:
                    continue
                alt = dist[u] + matrix[u][j]
                if alt < dist[j]:
                    dist[j] = alt
                    previous[j] = u

        return (dist,route_list)

    def calc_routes(self):
        """
        With dijkstra algorithm builds the route matrix in the whole topology
        """
        matrix = self.make_adjacency_matrix()
        #print "Adjacency matrix: " + str(matrix)
        route_matrix = [] #np.matrix((self.dim,self.dim),dtype=Route)
        for i in range(0,self.dim):
            #previous = np.zeros((1,self.dim),dtype=np.int)
            (dist, route_list) = self.dijkstra(matrix,i)
           # print previous
            route_matrix.append([])
            for j in range(0,self.dim):
                rt = Route(dist[j],route_list[j])
                route_matrix[i].append(rt)
        return route_matrix

    @staticmethod
    def build_distances(bw_hist):
        """
        Takes the information about the weights on edges
        and builds the matrix of distances between nodes.
        """
        # assuming that edge_list has changed after TrafficGen
        route_matrix = bw_hist.route_matrix
        print "Route matrix " + str(route_matrix)
        edge_dict = bw_hist.edge_dict
        dim = len(route_matrix)
        dist = [[0 for x in range(0,dim)] for y in range(0,dim)]
        for i in range(0,dim):
            for j in range(0,dim):
                route = route_matrix[i][j].route
                route_sum = 0
                for k in range(0,len(route)-1):
                    (v1,v2) = (route[k],route[k+1])
                    #if edge_dict.has_key((v1,v2)):
                    route_sum += edge_dict[(v1,v2)].sim_con_total
                    #else:
                dist[i][j] = route_sum
        return dist

    @staticmethod
    def prepare_priority_list(task,node_list):
        """
        Takes the information about the task
        And constructs the list of pairs : (<node>,<priority>)
        """
        # construct (<storage>,<priority> list)
        st_dep_list = []
        for x in node_list:
            if type(x) is Node.Storage:
                st_dep_list.append((x.id,task.storage_priority))
        # construct public priority list
        pub_dep_list = []
        for x in node_list:
            if type(x) is Node.NetworkNode:
               pub_dep_list.append((x.id,task.public_priority))
        # append to vm dep_list
        priorities = []
        priorities.extend(task.vm_dep_list)
        priorities.extend(st_dep_list)
        priorities.extend(pub_dep_list)
        return priorities

    @staticmethod
    def schedule(dist,task,node_list):
        """
        Simple scheduler. For every appropriate node (Compute node)
        finds the max the prior nodes
        """
        priorities = Scheduler.prepare_priority_list(task,node_list)
        min_dist = sys.maxint
        min_glob = sys.maxint
        min_id = -1
        weight_list = {}
        for node in node_list:
            if not isinstance(node, Node.ComputeNode):
                continue
            max_route = 0
            for prior in priorities:
                traf = dist[node.id][prior[0]]*prior[1] + dist[prior[0]][node.id]*prior[1]
                print traf
                if traf > max_route: # We are searching for maximum traffic on route link
                    max_route = traf
            weight_list[node.id] = max_route
            #if max_route < min_glob:
            #    min_glob = max_route
            #    min_id = node.id
            #    sum += dist[node.id][prior[0]]*prior[1] # the sum of <distance to prior node> * <priority of node>
            # sys.stdout.write("For node " + str(node.id) + " distance is " + str(sum) + "\n") # debug line
            #if sum < min_dist:
            #    min_dist = sum
            #    min_id = node.id
        return weight_list


    def print_route(self, route_matrix):
        for i in range(0,self.dim):
            for j in range(0,self.dim):
                sys.stdout.write("From " + str(i) + " to " + str(j) + " dist " + str(route_matrix[i][j].dist) + " Route: ")
                print route_matrix[i][j].route

class Route:

    def __init__(self,dist,route):
        self.dist = dist
        self.route = route

    def __repr__(self):
        return "<Route: %s Distance: %s" % (self.route, self.dist)


