__author__ = 'ash'

#import socket
import threading
import time
import SocketServer
import YamlDoc
import BandwidthHistory
import Node
import os


class Packet:
    """
    Class describes the packet info
    """

    def __init__(self, src, dst, length):
        self.src = src
        self.dst = dst
        self.len = length

class TrafficServer:

    def __init__(self):
        self.start_time = 0
        self.refresh_time = 2
        self.bw_id = 0
        self.traffic_stat = dict()

        self.get_topology()
        self.bw_hist = BandwidthHistory.BandwidthHistory(self.node_list,self.edge_list)

        self.router_id = self.get_router_id()
        self.node_dict = self.get_node_dict()


    def launch(self,port):
        HOST, PORT ='0.0.0.0', port
        server = MyThreadedTCPServer((HOST, PORT),MyTCPHandler)
        server.traffic = self
        server_thread = threading.Thread(target=server.serve_forever)
        #server_thread.daemon = True
        server_thread.start()
        start_time = time.clock()
        print("Server started!")

    def get_topology(self):
        yd = YamlDoc.YamlDoc('current-topology/nodes.yaml','current-topology/edges.yaml')
        self.node_list = yd.node_list
        self.edge_list = yd.edge_list

    def get_node_dict(self):
        node_dict = dict()
        for x in self.node_list:
            if not isinstance(x,Node.Switch):
                node_dict[x.ip_addr] = x.id
        return node_dict

    def get_router_id(self):
        for x in self.node_list:
            if isinstance(x,Node.Router):
                return x.id
        print "No router found"


class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.hostname = self.request.getsockname()[0]
        traffic_server = self.traffic_stat
        print 'Connected: ' + str(self.request.getsockname())
        while True:
            capt_time = time.clock()
            if capt_time - traffic_server.start_time > traffic_server.refresh_time:
                self.process_bandwidth(capt_time)
                traffic_server.bw_id += 1
                traffic_server.start_time = capt_time
                traffic_server.traffic_stat.clear()
            data = self.get_data()
            if len(data) < 5:
                continue
            self.handle_data(data)

    def handle_data(self,data):
        traffic_records = data.split(',')
        for i in range(0,len(traffic_records)-1):
            traf = traffic_records[i]
            split_data = traf.split('|')

            src = split_data[0]
            if src not in self.traffic.node_dict:
                src_id = self.traffic.router_id
            else:
                src_id = self.traffic.node_dict[src]

            dst = split_data[1]
            if dst not in self.traffic.node_dict:
                dst_id = self.traffic.router_id
            else:
                dst_id = self.traffic.node_dict[dst]

            leng = split_data[2]

            pk = Packet(src,dst,leng)
        #	print "Packet handled: Src: " + src + " Dst: " + dst + " Length: " + leng
            if (src_id,dst_id) not in self.traffic.traffic_stat:
                self.traffic.traffic_stat[(src_id,dst_id)] = 0
            self.traffic.traffic_stat[(src_id,dst_id)] += leng

    def process_bandwidth(self,capt_time):
        print "Bandwidth Refresh"
        os.system("clear")
        for k in self.traffic.traffic_stat.keys():
            bandwidth = self.traffic.traffic_stat[k] / (capt_time - self.traffic.start_time)
            (src,dst) = k
            self.traffic.bw_hist.append((src,dst),bandwidth,capt_time,self.traffic.bw_id)
            print "Src: " + src + " Dst: " + dst + " Bandwidth: " + bandwidth
		 	

    def get_data(self):
        data = self.request.recv(1024)
        print("{}: data accepted: {}".format(self.hostname, data))
        return data


class MyThreadedTCPServer(SocketServer.ThreadingMixIn,
        SocketServer.TCPServer):
    pass

#if __name__ =="__main__":
ts = TrafficServer()
ts.get_topology()
ts.launch(12345)
