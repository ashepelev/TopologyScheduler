__author__ = 'ash'


import yaml

import GraphDrawer
import Edge
import State
import Scheduler

import TrafficGen
import BandwidthHistory

stream_nodes = file('topology-examples/nodes1.yaml','r')
#print yaml.load(stream)
#print yaml.dump()

#print yaml.dump([Switch(0,[]),ComputeNode(1,[0],"example1.com"),CloudController(2,[0],"example0.com")])

stream_edges = file('topology-examples/edges1.yaml','r')

node_list = yaml.load(stream_nodes)
edge_list = yaml.load(stream_edges)

#st = State.State(node_list,edge_list)
#st.setState() # random state

#print node_list

#sched = Scheduler.Scheduler(node_list,edge_list)
#route_matrix = sched.calc_routes()
#sched.print_route(route_matrix)
#print matr

bwhist = BandwidthHistory.BandwidthHistory(node_list,edge_list)
trgen = TrafficGen.TrafficGen(node_list,bwhist)

trgen.generator()


stream_nodes.close()
stream_edges.close()

#trgen = TrafficGen.TrafficGen(node_list)
#trgen.generator()

dist = Scheduler.Scheduler.build_distances(bwhist)
task = Scheduler.Task.example_task()
print Scheduler.Scheduler.schedule(dist,task,node_list)

gr = GraphDrawer.GraphDrawer(node_list,edge_list)
graph = gr.get_edges()
labels = gr.get_labels()
gr.draw_graph(graph,labels=labels, graph_layout='spring',draw_bandwidth='avg')

exit()