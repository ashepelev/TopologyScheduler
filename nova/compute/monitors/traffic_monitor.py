from nova.scheduler.weights.TopologyWeigher import YamlDoc, Node

__author__ = 'ash'

import socket
import fcntl
from struct import *
import pcapy
from time import sleep
from time import time
import shlex
from subprocess import Popen, PIPE, STDOUT
from threading import Timer
from threading import Thread

from nova.conductor import api as conductor_api
from nova import context
from nova.openstack.common import log as logging


traffic_stat = dict()
LOG = logging.getLogger("nova-compute")


class ClientTraffic(Thread):

    def __init__(self,sniff_int,log,topology_desc_path):
        Thread.__init__(self)
        self.daemon = True
        self.topology_desc_path = topology_desc_path
        self.get_topology_nodes()
        self.node_dict = self.get_node_dict()
        self.router_id = self.get_router_id()
        self.interface = sniff_int
        self.ip_addr = self.get_ip_address(sniff_int)

        self.bw_id = 0
        self.refresh_time = 10
        self.my_id = self.get_my_id()
        self.time_to_send = False

        self.ping_info = dict()
        self.log = log
        self.conductor = conductor_api.API()

        self.router_ip = self.get_router_ip()

        #greenthread.spawn(self.launch)

        #print "Client initiated"

    def run(self):
        #print "Try to launch"
        #thread = Thread(target=self.launch())
        #thread.daemon = True
        #thread.start()
        self.launch()

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
        yd = YamlDoc.YamlDoc(self.topology_desc_path + 'nodes.yaml',self.topology_desc_path +  'edges.yaml')
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

    def get_router_ip(self):
        for x in self.node_list:
            if isinstance(x, Node.Router):
                return x.ip_addr
        return False

    def get_hosts_id(self,src_ip,dst_ip):
        #traffic_server = self.server.traffic
        if src_ip not in self.node_dict:
            src_id = self.router_id
        else:
            src_id = self.node_dict[src_ip]
        if dst_ip not in self.node_dict:
            dst_id = self.router_id
        else:
            dst_id = self.node_dict[dst_ip]
        return (src_id,dst_id)

    def get_my_id(self):
        return self.node_dict[self.ip_addr]

    def process_ping(self):
        self.send_ping()

    def send_ping(self):
        #msgs = "Ping:"
        self.log.debug("Sending ping")
        for key in self.ping_info:
            ping = self.ping_info[key]
            (src_id,dst_id) = self.get_hosts_id(ping.src,ping.dst)
            ping_value = ping.result
            resources = {}
            resources['src'] = src_id
            resources['dst'] = dst_id
            resources['latency'] = ping_value
            self.conductor.ping_add(self.context,resources)
            #msg = str(src_id)+"|"+ str(dst_id) + "|" + str(ping_value) + ','
            #msgs += msg
        #msgs = msgs.rstrip(',')
        #print "Sending: " + msgs
        #self.socket.sendall(msgs)

    def handle_new_ips(self,packet):
        if packet.src == self.ip_addr:
            dst = packet.dst
        else:
            dst = packet.src
        if dst not in self.node_dict:
            dst = self.router_ip
        if not (self.ip_addr,dst) in self.ping_info:
            self.ping_info[self.ip_addr,dst] = ip_ping(self.ip_addr,dst)
            self.ping_info[self.ip_addr,dst].start()

    def handle_packet(self,packet):
        self.handle_new_ips(packet)
        (src_id,dst_id) = self.get_hosts_id(packet.src,packet.dst)
        if not (src_id,dst_id) in traffic_stat:
            #self.process_ping(packet)
            nl = NetworkLoad()
            nl.inc(packet.length)
            traffic_stat[(src_id,dst_id)] = nl
        else:
            traffic_stat[(src_id,dst_id)].inc(packet.length)

    def process_bandwidth(self):
        #os.system("clear")
        #print "Process bandwidth: Len Keys: " + str(len(traffic_stat.keys()))
        for k in traffic_stat.keys():
            bandwidth = traffic_stat[k].count / self.refresh_time
            (src,dst) = k
            #self.bw_hist.append((src,dst),bandwidth,capt_time,self.bw_id)
            traffic_stat[k].bandwidth = bandwidth
            #latency = traffic_stat[k].ping
            #print "Src: " + str(src) + " Dst: " + str(dst) + " Bandwidth: " + str(bandwidth)
        #sys.stdout.flush()

    def send_traffic(self):
        #msgs = "Traffic:"
        #self.log.debug("Sending...")
        for link in traffic_stat.keys():
            (src_id,dst_id) = link
            #count = traffic_stat[link].count
            bandwidth = traffic_stat[link].bandwidth
            resources = {}
            resources['src'] = src_id
            resources['dst'] = dst_id
            resources['bytes'] = bandwidth
            resources['m_id'] = self.bw_id
            #msg = str(src_id) + '|' + str(dst_id) + '|' + str(bandwidth) + ','
            #msgs += msg
            #self.log.debug("Send to conductor")
            self.conductor.traffic_add(self.context, resources)
        #print "Sending: " + msgs
        #msgs = msgs.rstrip(',') # delete last comma
        #conductor.traffic_add(self.context,)
        #self.socket.send(msgs)
        self.bw_id += 1
        traffic_stat.clear()



    def refresh_send(self):
        self.time_to_send = True
        self.log.debug("Settted")
        self.process_bandwidth()
        self.send_traffic()

    #def launch(self,hostname,server_port):
    def launch(self):
        #print "Launched!"
        #self.server_port = server_port
        #ipaddr = socket.gethostbyname(hostname)
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket = s
        #s.connect((hostname, self.server_port))
        #self.log.debug("LAUNCHED")
        self.context = context.get_admin_context()
        #print "Connected!"
        #print "Listen on interface: " + self.interface
        cap = pcapy.open_live(self.interface,65536,1,0)
        self.start_time = time()
        #rt_traffic = RepeatedTimer(2,self.refresh_send) # Sending traffic
        rt_ping = RepeatedTimer(4,self.process_ping) # Sending ping
        #greenthread.sleep(0)
        while (1) :
            #sys.stdout.write("1")
            (header, packet) = cap.next()
            #sys.stdout.write("1")
            #sys.stdout.flush()
            #capt_time = clock()
            (src,dst,leng,res) = self.parse_packet(packet)
            if not res:
                #print "Not res"
                continue
            pk = Packet(src,dst,leng)
            #print "Captured packet. Src: " + str(src) + " Dst: " + str(dst) + " Length: " + str(leng)
            self.handle_packet(pk)
            if time() - self.start_time > self.refresh_time:
                sleep(0.01)
                self.start_time = time()
                #print "Clock!"
                #self.log.debug("!!!!!!!!!!!!TIMER_READY!!!!!!!!!!!!!!!!")
                self.time_to_send = False
                self.process_bandwidth()
                self.send_traffic()

        #s.close()

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

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class ip_ping(Thread):
   def __init__ (self,src,dst):
        Thread.__init__(self)
        self.src = src
        self.dst = dst
        self.result = -1
        self.repeat = 4
        #self.__successful_pings = -1

   def run(self):
        while 1:
            src = self.src
            host = self.dst
            host = host.split(':')[0]
            #print "Ping launched"
            LOG.debug('Launching ping')
            cmd = "fping {host} -C 1 -q".format(host=host)
            res = [float(x) for x in self.get_simple_cmd_output(cmd).strip().split(':')[-1].split() if x != '-']
            if len(res) > 0:
                result = sum(res) / len(res)
            else:
                result = 9999.0
            #print "Result: " + str((src,host,result))
            self.result = result
            sleep(self.repeat)

   def get_simple_cmd_output(self,cmd, stderr=STDOUT):
        """
        Execute a simple external command and get its output.
        """
        args = shlex.split(cmd)
        return Popen(args, stdout=PIPE, stderr=stderr).communicate()[0]

   def ready(self):
       return self.result != -1

#conductor_api = conductor.API()
client = ClientTraffic("eth0.800",LOG,'/opt/stack/TopologyScheduler/current-topology/')
client.start()