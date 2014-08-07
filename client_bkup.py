from nova.scheduler.weights.TopologyWeigher import YamlDoc, Node

__author__ = 'ash'

import socket
import fcntl
from struct import *
import pcapy
import sys
from time import clock
from os import system
import shlex
from subprocess import Popen, PIPE, STDOUT
from multiprocessing import Pool

traffic_stat = dict()

def get_simple_cmd_output(cmd, stderr=STDOUT):
        """
        Execute a simple external command and get its output.
        """
        args = shlex.split(cmd)
        return Popen(args, stdout=PIPE, stderr=stderr).communicate()[0]

def get_ping_time(addr_pair):
    (src,host) = addr_pair
    host = host.split(':')[0]
    print "Ping launched"
    cmd = "fping {host} -C 1 -q".format(host=host)
    res = [float(x) for x in get_simple_cmd_output(cmd).strip().split(':')[-1].split() if x != '-']
    if len(res) > 0:
        result = sum(res) / len(res)
    else:
        result = 999999
    print "Result: " + str(result)
    return (src,host,result)

def write_ping(ping_res):
    (src_id,dst_id,ping) = ping_res
    traffic_stat[(src_id,dst_id)].ping = float(ping)
    print "Pinged: " + str(ping)


class ClientTraffic:

def __init__(self,sniff_int):
    self.get_topology_nodes()
    self.node_dict = self.get_node_dict()
    self.router_id = self.get_router_id()
    self.interface = sniff_int
    self.ip_addr = self.get_ip_address(sniff_int)

    self.bw_id = -1
    self.refresh_time = 1
    self.my_id = self.get_my_id()

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
        if not isinstance(x, Node.Switch):
            node_dict[x.ip_addr] = x.id
    return node_dict

def get_router_id(self):
    for x in self.node_list:
        if isinstance(x, Node.Router):
            return x.id
    print "No router found"

def get_hosts_id(self,packet):
    #traffic_server = self.server.traffic
    if packet.src not in self.node_dict:
        src_id = self.router_id
    else:
        src_id = self.node_dict[packet.src]
    if packet.dst not in self.node_dict:
        dst_id = self.router_id
    else:
        dst_id = self.node_dict[packet.dst]
    return (src_id,dst_id)

def get_my_id(self):
    return self.node_dict[self.ip_addr]

def process_ping(self,packet):
    pool = Pool(processes=1)
    if packet.src == self.ip_addr:
        dst = packet.dst
    else:
        dst = packet.src
    print "Dst ping: " + dst
    pool.apply_async(get_ping_time,(self.ip_addr,dst),callback=write_ping)

def handle_packet(self,packet):
    (src_id,dst_id) = self.get_hosts_id(packet)
    if not (src_id,dst_id) in traffic_stat:
        self.process_ping(packet)
        nl = NetworkLoad()
        nl.inc(packet.length)
        traffic_stat[(src_id,dst_id)] = nl
    else:
        traffic_stat[(src_id,dst_id)].inc(packet.length)

def process_bandwidth(self,capt_time):
    system("clear")
    print "Process bandwidth: Len Keys: " + str(len(traffic_stat.keys()))
    for k in traffic_stat.keys():
        bandwidth = traffic_stat[k].count / (capt_time - self.start_time)
        (src,dst) = k
        #self.bw_hist.append((src,dst),bandwidth,capt_time,self.bw_id)
        traffic_stat[k].bandwidth = bandwidth
        latency = traffic_stat[k].ping
        print "Src: " + str(src) + " Dst: " + str(dst) + " Bandwidth: " + str(bandwidth) + " Latency: " + str(latency)

def process_traffic(self,capt_time,socket):
    msgs = self.prepare_message()
    #socket.send(msgs)
    self.bw_id += 1
    self.start_time = capt_time
    traffic_stat.clear()

def prepare_message(self):
    msgs = ""
    for link in traffic_stat.keys():
        (src_id,dst_id) = link
        #count = traffic_stat[link].count
        bandwidth = traffic_stat[link].bandwidth
        msg = str(src_id) + '|' + str(dst_id) + '|' + str(bandwidth) + ','
        msgs += msg
    #print "Sending: " + msgs
    msgs = msgs.rstrip(',') # delete last comma
    return msgs


def launch(self,hostname,server_port):
    self.server_port = server_port
    #ipaddr = socket.gethostbyname(hostname)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.connect((hostname, self.server_port))
    print "Connected!"
    print "Listen on interface: " + self.interface
    cap = pcapy.open_live(self.interface,65536,1,0)
    self.start_time = clock()
    while (1) :
        (header, packet) = cap.next()
        sys.stdout.write("1")
        capt_time = clock()
        (src,dst,leng,res) = self.parse_packet(packet)
        if not res:
           continue
        pk = Packet(src,dst,leng)
        self.handle_packet(pk)
        #print str(capt_time) + " - " + str(self.start_time)
        if capt_time - self.start_time > self.refresh_time:
            print "Refreshed!"
            self.process_bandwidth(capt_time)
            self.process_traffic(capt_time,s)

        #msg = str(src) + '|' + str(dst) + '|' + str(leng) + ','
        #print "Sending: " + msg
        #s.sendall(bytes(msg,'utf8'))
        #s.sendall(msg)
    s.close()

class Packet:
    """
    Class describes the packet info
    """

    def __init__(self, src, dst, length):
        self.src = src
        self.dst = dst
        self.length = length

class NetworkLoad:

    def __init__(self):
        self.count = 0
        self.error = 0
        self.metric_ind = 0
        self.error_ind = 0
        self.metrics = ['B', 'KB', 'MB', 'GB', 'TB']
        self.bandwidth = 0
        self.ping = -1

    def inc(self,leng):
        self.count += leng

    def sum_up(self):
        while self.count >= 1024:
            # error obtaining not significantly TO DO
            self.count /= 1024
            self.metric_ind += 1

client = ClientTraffic("eth0.800")
client.launch("10.2.0.51",12345)
