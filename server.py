__author__ = 'ash'

#import socket
import threading
import time
import SocketServer
import YamlDoc
import BandwidthHistory
import Node
import os




class TrafficServer:

    def __init__(self):
        self.start_time = 0
        self.refresh_time = 3
        self.bw_id = 0
        self.traffic_stat = dict()

        self.get_topology()
        self.bw_hist = BandwidthHistory.BandwidthHistory(self.node_list,self.edge_list)

        self.router_id = self.get_router_id()
        self.node_dict = self.get_node_dict()

        self.previous_packet_data = dict()


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
        self.client_ip = self.request.getpeername()[0]
        traffic_server = self.server.traffic
        print 'Connected: ' + str(self.client_ip)
        while True:
            data = self.get_data()
            if len(data) < 3:
                continue
            capt_time = time.clock()
            self.handle_data(data)

    def handle_data(self,data):
        if data.startswith("Ping:"):
            self.process_ping(data)
        elif data.startswith("Traffic:"):
            self.process_traffic(data)


            """
            if len(split_data) < 3:
                remains_data = True
                traffic_server[self.hostname] = remains_data
            else:

            """
    def process_traffic(self,data):
        data = data.lstrip("Traffic:")
        traffic_records = data.split(',')
        for traffic_record in traffic_records:
            if traffic_record == '':
                continue
            traffic_server = self.server.traffic
            split_data = traffic_record.split('|')
            (src_id,dst_id,traf) = self.get_traffic_info(split_data)
            #print "Traffic split data: " + str(split_data)
            print "Recieved traffic: " + str((src_id,dst_id,traf))
            #traffic_server.bw_hist.append((src_id,dst_id),traf,traffic_server.bw_id)

    def process_ping(self,data):
        data = data.lstrip("Ping:")
        traffic_records = data.split(',')
        for traffic_record in traffic_records:
            if traffic_record == '':
                continue
            traffic_server = self.server.traffic
            split_data = traffic_record.split('|')
            (src_id,dst_id,ping) = self.get_ping_info(split_data)
            print "Recieved ping: " + str((src_id,dst_id,ping))
            #traffic_server.bw_hist.append((src_id,dst_id),bw,traffic_server.bw_id)

    def get_node_ids(self,split_data):
        traffic_server = self.server.traffic
        src_id = int(split_data[0])
        dst_id = int(split_data[1])
        # Client already resolved the ips
        """if src not in traffic_server.node_dict:
            src_id = traffic_server.router_id
        else:
            src_id = int(src)
        dst = split_data[1]
        if dst not in traffic_server.node_dict:
            dst_id = traffic_server.router_id
        else:
            dst_id = int(dst)
        """
        return (src_id,dst_id)

    def get_traffic_info(self,split_data):
        (src_id,dst_id) = self.get_node_ids(split_data)
        leng = float(split_data[2])
        return (src_id,dst_id,leng)

    def get_ping_info(self,split_data):
        (src_id,dst_id) = self.get_node_ids(split_data)
        ping = float(split_data[2])
        return (src_id,dst_id,ping)

    def process_bandwidth(self,capt_time):
        traffic_server = self.server.traffic
        print "Bandwidth Refresh"
        #os.system("clear")
        for k in traffic_server.traffic_stat.keys():
            #bandwidth = traffic_server.traffic_stat[k] / (capt_time - traffic_server.start_time)
            (src,dst) = k
            traffic_server.bw_hist.append((src,dst),traffic_server.traffic_stat[k].bandwidth,capt_time,traffic_server.bw_id)
            print "Src: " + src + " Dst: " + dst + " Bandwidth: " + traffic_server.traffic_stat[k].bandwidth


    def get_data(self):
        data = ""
        #while self.request.recv != 0:
	#    print "Recieved!"
        data += self.request.recv(1024)
        print("{}: data accepted: {}".format(self.client_ip, data))
        return data


class MyThreadedTCPServer(SocketServer.ThreadingMixIn,
        SocketServer.TCPServer):
    pass

#if __name__ =="__main__":
ts = TrafficServer()
ts.get_topology()
ts.launch(12345)
