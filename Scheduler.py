__author__ = 'ash'

import numpy as np
from sets import Set
import sys

class Task:

    def __init__(self,vm_dep_list,storage_priority,public_priority):
        self.vm_dep_list = vm_dep_list
        self.storage_priority = storage_priority
        self.public_priority = public_priority

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
        min = sys.maxint
        minind = -1
        for elem in q:
            if (dist[elem] < min):
                min = dist[elem]
                minind = elem
        return minind

    def dijkstra(self,matrix,src):
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
        matrix = self.make_adjacency_matrix()
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

    def print_route(self, route_matrix):
        for i in range(0,self.dim):
            for j in range(0,self.dim):
                sys.stdout.write("From " + str(i) + " to " + str(j) + " dist " + str(route_matrix[i][j].dist) + " Route: ")
                print route_matrix[i][j].route




class Route:

    def __init__(self,dist,route):
        self.dist = dist
        self.route = route


