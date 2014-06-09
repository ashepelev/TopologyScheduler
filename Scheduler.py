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
        self.infinity = 1000000
        self.undefined = -1

    def make_adjacency_matrix(self):
        matrix = np.matrix(np.zeros((self.dim,self.dim),dtype=np.int))
        for edge in self.edge_list:
            pair = edge.node_pair
            matrix[pair[0],pair[1]] = 1
            matrix[pair[1],pair[0]] = 1
        return matrix

    def min_distance(self,dist,q):
        min = sys.maxint
        minind = -1
        for i in range(0,len(q)):
            if (dist[q[i]] < min):
                min = dist[q[i]]
                minind = q[i]
        return minind

    def dijkstra(self,matrix,src,previous):
        dist = [0]* self.dim
        previous = [0] * self.dim

        for i in range(0,self.dim):
            dist[i] = self.infinity
            previous[i] = self.undefined

        dist[src] = 0
        q = Set()
        for i in range(0,self.dim):
            q.add(i)

        while (len(q) > 0):
            if (len(q) == self.dim):
                u = src
            else:
                u = self.minDistance(dist,q)
            q.remove(u)
            
            if (dist[i] == self.infinity):
                break
            for j in range(0,self.dim):
                if (matrix[u,j] == self.infinity):
                    continue
                alt = dist[i] + matrix[u,j]
                if (alt < dist[j]):
                    dist[j] = alt
                    previous[j] = u
        return (dist,previous)

    def calc_routes(self):
        matrix = self.make_adjacency_matrix()
        route_matrix = [[0] * self.dim] * self.dim#np.matrix((self.dim,self.dim),dtype=Route)
        for i in range(0,self.dim):
            #previous = np.zeros((1,self.dim),dtype=np.int)
            (dist, previous) = self.dijkstra(matrix,i,previous)
            print previous
            for j in range(0,self.dim):
                route = []
                u = j
                while previous[u] != self.undefined:
                    route.append()
                    u = previous[u]
                rt = Route(dist[j],route)
                route_matrix[i,j] = rt

    def print_route(self, route_matrix):
        for i in range(0,self.dim):
            for j in range(0,self.dim):
                sys.stdout.write("From" + str(i) + " to " + str(j) + " dist " + route_matrix[i,j].dist + " Route: ")
                print route_matrix[i,j].route


class Route:

    def __init__(self,dist,route):
        self.dist = dist
        self.route = route


