__author__ = 'ash'

import socket
import fcntl
from struct import *
import datetime
import pcapy
import sys
import YamlDoc
import Node
from math import pow
from time import clock
from os import system


class ClientTraffic:

    def __init__(self,sniff_int):
        self.get_topology_nodes()
        self.node_dict = self.get_node_dict()
        self.router_id = self.get_router_id()
        self.interface = sniff_int
        self.ip_addr = self.get_ip_address(sniff_int)
        self.traffic_stat = dict()

        self.bw_id = -1
        self.refresh_time = 1

    def eth_addr (a) :
        b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]), ord(a[4]) , ord(a[5]))
        return b

    def get_ip_address(self,ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            pack('256s', ifname[:15])
        )[20:24])

    #function to parse a packet
    def parse_packet(self,packet) :

        #parse ethernet header
        eth_length = 14

        eth_header = packet[:eth_length]
        eth = unpack('!6s6sH' , eth_header)
        eth_protocol = socket.ntohs(eth[2])
        #print 'Destination MAC : ' + eth_addr(packet[0:6]) + ' Source MAC : ' + eth_addr(packet[6:12]) + ' Protocol : ' + str(eth_protocol)

        #Parse IP packets, IP Protocol number = 8
        res = False
        if eth_protocol == 8 :
            #Parse IP header
            #take first 20 characters for the ip header
            ip_header = packet[eth_length:20+eth_length]

            #now unpack them :)
            iph = unpack('!BBHHHBBH4s4s' , ip_header)

            version_ihl = iph[0]
            #version = version_ihl >> 4
            ihl = version_ihl & 0xF
            iph_length = ihl * 4

            #ttl = iph[5]
            #protocol = iph[6]
            s_addr = socket.inet_ntoa(iph[8]);
            d_addr = socket.inet_ntoa(iph[9]);

            protocol = iph[6]
            res = True
            if protocol == 6:
                t = iph_length + eth_length
                tcp_header = packet[t:t+20]

                #now unpack them :)
                tcph = unpack('!HHLLBBHHH' , tcp_header)
                doff_reserved = tcph[4]
                tcph_length = doff_reserved >> 4
                h_size = eth_length + iph_length + tcph_length * 4
                data = packet[h_size:]
                if len(data)>2:
                    if data.startswith(self.ip_addr): # if it is our traffic stat packets
                        res = False
                #print 'Version : ' + str(version) + ' IP Header Length : ' + str(ihl) + ' TTL : ' + str(ttl) + ' Protocol : ' + str(protocol) + ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr)
                #print ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr) + ' Length : ' + str(len(packet))
                return (s_addr,d_addr,len(packet),res)
        return (0,0,0,False)

    def get_topology_nodes(self):
        yd = YamlDoc.YamlDoc('current-topology/nodes.yaml','current-topology/edges.yaml')
        self.node_list = yd.node_list

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

    def get_hosts_id(self,packet):
        traffic_server = self.server.traffic
        if packet.src not in self.node_dict:
            src_id = self.router_id
        else:
            src_id = self.node_dict[packet.src]
        if packet.dst not in self.node_dict:
            dst_id = self.router_id
        else:
            dst_id = self.node_dict[packet.dst]
        return (src_id,dst_id)

    def handle_packet(self,packet):
        (src_id,dst_id) = self.get_hosts_id(packet)
        if not (src_id,dst_id) in self.traffic_stat:
            nl = NetworkLoad()
            nl.inc(packet.length)
            self.traffic_stat[(src_id,dst_id)] = nl
        else:
            self.traffic_stat[(src_id,dst_id)].inc(packet.length)

    def process_bandwidth(self,capt_time):
        print "Bandwidth Refresh"
        system("clear")
        for k in self.traffic_stat.keys():
            bandwidth = self.traffic_stat[k] / (capt_time - self.start_time)
            (src,dst) = k
            self.bw_hist.append((src,dst),bandwidth,capt_time,self.bw_id)
            print "Src: " + src + " Dst: " + dst + " Bandwidth: " + bandwidth

    def process_traffic(self,capt_time,socket):
        msgs = self.prepare_message()
        socket.sendall(msgs)
        self.bw_id += 1
        self.start_time = capt_time
        self.traffic_stat.clear()

    def prepare_message(self):
        msgs = ""
        for link in self.traffic_stat.keys():
            (src_id,dst_id) = link
            count = self.traffic_stat[link].count
            msg = str(src_id) + '|' + str(dst_id) + '|' + count + ','
            msgs.add(msg)
        #msgs.rstrip(',') # delete last comma
        return msgs


    def launch(self,hostname,server_port):
        port = server_port
        #ipaddr = socket.gethostbyname(hostname)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostname, port))
        print "Connected!"
        print "Listen on interface: " + self.interface
        cap = pcapy.open_live(self.interface,65536,1,0)

        self.start_time = clock()
        while (1) :
            (header, packet) = cap.next()
            capt_time = clock()
            if capt_time - self.start_time > self.refresh_time:
                self.process_bandwidth(capt_time)
                self.process_traffic(capt_time,s)

            (src,dst,leng,res) = self.parse_packet(packet)
            if not res:
               continue
            pk = Packet(src,dst,leng)
            self.handle_packet(packet)
            msg = str(src) + '|' + str(dst) + '|' + str(leng) + ','
            print "Sending: " + msg
            #s.sendall(bytes(msg,'utf8'))
            s.sendall(msg)
        s.close()

class Packet:
    """
    Class describes the packet info
    """

    def __init__(self, src, dst, length):
        self.src = src
        self.dst = dst
        self.len = length

class NetworkLoad:

    def __init__(self):
        self.count = 0
        self.error = 0
        self.metric_ind = 0
        self.error_ind = 0
        self.metrics = ['B', 'KB', 'MB', 'GB', 'TB']

    def inc(self,leng):
        self.count += leng

    def sum_up(self):
        while self.count >= 1024:
            # error obtaining not significantly TO DO
            self.count /= 1024
            self.metric_ind += 1

client = ClientTraffic("eth0.800")
client.launch("10.2.0.51",12345)