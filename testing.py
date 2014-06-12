__author__ = 'ash'


import yaml

import GraphDrawer
import Edge
import State
import Scheduler

stream_nodes = file('topology-examples/nodes1.yaml','r')
#print yaml.load(stream)
#print yaml.dump()

#print yaml.dump([Switch(0,[]),ComputeNode(1,[0],"example1.com"),CloudController(2,[0],"example0.com")])

stream_edges = file('topology-examples/edges1.yaml','r')

node_list = yaml.load(stream_nodes)
edge_list = yaml.load(stream_edges)

st = State.State(node_list,edge_list)
st.setState() # random state

#print node_list

sched = Scheduler.Scheduler(node_list,edge_list)
route_matrix = sched.calc_routes()
sched.print_route(route_matrix)
#print matr

stream_nodes.close()
stream_edges.close()



gr = GraphDrawer.GraphDrawer(st.node_list,st.edge_list)
graph = gr.get_edges()
labels = gr.get_labels()
gr.draw_graph(graph,labels=labels, graph_layout='spring',draw_bandwidth='avg')

exit()