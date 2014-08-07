__author__ = 'ash'

from oslo.config import cfg

from nova import exception
from nova.scheduler import utils
from nova.scheduler import weights
from nova.db import api as db_api
import TopologyWeigher.YamlDoc as YamlDoc
import TopologyWeigher.utils as topoutils
from TopologyWeigher.BandwidthHistory import BandwidthHistory as BandwidthHistory
from  TopologyWeigher.Scheduler import Scheduler as Scheduler
from  TopologyWeigher.Scheduler import Task as Task

topology_weight_opts = [
        cfg.StrOpt('topology_description_path',
                   default=None,
                   help='Full path to directory with '
                        ' describing of the topology.'
                        'The directory should have '
                        'nodes.yaml and edges.yaml files.')
        ]

CONF = cfg.CONF
CONF.register_opts(topology_weight_opts)


class TopologyWeighedObject(weights.WeighedHost):
    def __init__(self, obj, weight):
        super(TopologyWeighedObject, self).__init__(obj,weight)

    def set_ip_id(self,ip_addr,id):
        self.obj.ip = ip_addr

    def set_id(self,id):
        self.obj.id = id

    @staticmethod
    def to_weight_list(weighed_obj_list,scheduler_dict,node_by_hostname):
        weights = []
        for obj in weighed_obj_list:
            weights.append(scheduler_dict[node_by_hostname[obj.obj.host].id])
        return weights

class TopologyWeigher(weights.BaseHostWeigher):

    minval = 0.0
    maxval = 1.0

    def weight_multiplier(self):
        return -1.0 # as more traffic and latency is worser
    #
    def _weigh_object(self, obj, weight_properties):
        pass

    def weigh_objects(self, weighed_obj_list, weight_properties):
        context = weight_properties['context']
        traffic_info = db_api.traffic_get_avg(context,3600)
        self.topology_desc_path = CONF.topology_description_path

        #print str(self.topology_desc_path)
        (self.node_list,self.edge_list) = topoutils.get_topology(self.topology_desc_path)
        node_dict = topoutils.get_node_dict_by_id(self.node_list)
        """
        endpoint_dict = topoutils.list_to_endpoints_dict(self.node_list)
        for x in weighed_obj_list:
            node = endpoint_dict[x.obj.host]
            #x.set_ip(node.ip_addr)
            #x.set_id(node.id)
            x.obj.ip = node.ip_addr
            x.obj.id = node.id
        """
        traffic = []
        bw_hist = BandwidthHistory(self.node_list,self.edge_list)
        print str(traffic_info)
        for tr in traffic_info:
            #print "Src: " + str(tr.src) + " Dst: " + str(tr.dst) + " Avg: " + str(tr.avg)
            (val,src,dst) = tr
            src = int(src)
            dst = int(dst)
            bw_hist.append((src,dst),val,0)
            #traf = topoutils.Traffic(src,dst,val)
            #traffic.append(traf)
        print bw_hist.edge_dict
        task = Task.example_task()
        dist = Scheduler.build_distances(bw_hist)
        print dist
        node_list_by_hostname = topoutils.list_to_endpoints_dict(self.node_list)

        weights = Scheduler.schedule(dist,task,self.node_list)
        print weights

        #node_by_id = topoutils.get_node_dict_by_id(self.node_list)

        return TopologyWeighedObject.to_weight_list(weighed_obj_list,weights,node_list_by_hostname)







