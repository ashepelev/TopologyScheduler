__author__ = 'ash'

import Node
import YamlDoc

from nova.openstack.common import log as logging

LOG = logging.getLogger(__name__)

def get_topology(path=None,nodes_file = "nodes.yaml", edges_file = "edges.yaml"):
    if path==None:
        LOG.error("No topology path specified for TopologyWeigher")
        return
    n_path = path + "/"
    yd = YamlDoc.YamlDoc(n_path + nodes_file,n_path+edges_file)
    return (yd.node_list,yd.edge_list)

def list_to_endpoints_dict(node_list):
    node_dict = {}
    for x in node_list:
        if isinstance(x,Node.ComputeNode):
            node_dict[x.hostname] = x
    return node_dict

def get_node_dict_by_id(node_list):
    node_dict = dict()
    for x in node_list:
        if isinstance(x,Node.Endpoint):
            node_dict[x.id] = x
    return node_dict

def get_node_dict(node_list):
    node_dict = dict()
    for x in node_list:
        if not isinstance(x, Node.Switch):
            node_dict[x.ip_addr] = x.id
    return node_dict

def get_router_id(node_list):
    for x in node_list:
        if isinstance(x, Node.Router):
            return x.id
    print "No router found"

def get_router_ip(node_list):
    for x in node_list:
        if isinstance(x, Node.Router):
            return x.ip_addr
    LOG.error("No router specified in topology-nodes description")

def get_hosts_id(src_ip,dst_ip,node_dict,router_id):
    #traffic_server = self.server.traffic
    if src_ip not in node_dict:
        src_id = router_id
    else:
        src_id = node_dict[src_ip]
    if dst_ip not in node_dict:
        dst_id = router_id
    else:
        dst_id = node_dict[dst_ip]
    return (src_id,dst_id)

def get_my_id(node_dict,my_ip):
    return node_dict[my_ip]