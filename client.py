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
import re
import Queue

traffic_stat = dict()


class ClientTraffic:

    def __init__(self,sniff_int):
        #self.get_topology_nodes()
        #self.node_dict = self.get_node_dict()
        #self.router_id = self.get_router_id()
        self.interface = sniff_int
        #self.ip_addr = self.get_ip_address(sniff_int)

        self.bw_id = -1
        self.refresh_time = 2
        #self.my_id = self.get_my_id()
        self.time_to_send = False

        self.ping_info = dict()

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
        msgs = "Ping:"
        for key in self.ping_info:
            ping = self.ping_info[key]
            (src_id,dst_id) = self.get_hosts_id(ping.src,ping.dst)
            ping_value = ping.result
            msg = str(src_id)+"|"+ str(dst_id) + "|" + str(ping_value) + ','
            msgs += msg
        msgs = msgs.rstrip(',')
        print "Sending: " + msgs
        #self.socket.sendall(msgs)

    def handle_new_ips(self,packet):
        if packet.src == self.ip_addr:
            dst = packet.dst
        else:
            dst = packet.src
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
            print "Src: " + str(src) + " Dst: " + str(dst) + " Bandwidth: " + str(bandwidth)
        #sys.stdout.flush()

    def send_traffic(self):
        msgs = "Traffic:"
        print "Sending traffic"
        for link in traffic_stat.keys():
            (src_id,dst_id) = link
            #count = traffic_stat[link].count
            bandwidth = traffic_stat[link].bandwidth
            msg = str(src_id) + '|' + str(dst_id) + '|' + str(bandwidth) + ','
            msgs += msg
        #print "Sending: " + msgs
        msgs = msgs.rstrip(',') # delete last comma
        self.socket.send(msgs)
        self.bw_id += 1
        traffic_stat.clear()


    def refresh_send(self):
        self.time_to_send = True

    def launch(self,hostname,server_port):
        self.server_port = server_port
        #ipaddr = socket.gethostbyname(hostname)
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket = s
        #s.connect((hostname, self.server_port))
        print "Connected!"
        print "Listen on interface: " + self.interface
        #cap = pcapy.open_live(self.interface,65536,1,0)
        cap = pcapy.open_live(self.interface,65536,1,0)
        #rt_traffic = RepeatedTimer(2,self.refresh_send) # Sending traffic
        data = Queue.Queue()
        #tcp = my_tcpdump("eth0",data)
        #tcp.start()
        self.start_time = time()
        #
        #rt_ping = RepeatedTimer(4,self.process_ping) # Sending ping
        while (1) :
            #sys.stdout.write("1")
            (header, packet) = cap.next()
            #sys.stdout.write("2")
            #sys.stdout.flush()
            #capt_time = clock()
            (src,dst,leng,res) = self.parse_packet(packet)
            if not res:
               continue
            pk = Packet(src,dst,leng)
            print "Captured " + src + " " + dst + " " + str(leng)

            #self.handle_packet(pk)
            print time()
            print self.start_time
            if time() - self.start_time > self.refresh_time:
                self.start_time = time()
                print "Clock!"
                #self.time_to_send = False
                #self.process_bandwidth()
                #self.send_traffic()



        return

        cmd = "tcpdump -n -nn -l -i eth0"
        args = shlex.split(cmd)
        # Here STP & ARP calls are not included
        p = re.compile(r'.*IP.(?P<src>[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*)\..*>.'
                       r'(?P<dst>[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*)\..*'
                       r'(length.(?P<len>[0-9]*)|\((?P<len2>[0-9]*)\))$')
        proc = Popen(args, stdout=PIPE, stderr=STDOUT)

        while (1):
            for line in iter(proc.stdout.readline,''):
                m = p.match(line)
                if not m:
                    continue
                if m.group('len') == None:
                    len = m.group('len2')
                else:
                    len = m.group('len')
                pd = (m.group('src'),m.group('dst'),len)

                if not pd:
                    #print "BAD LINE: " + line
                    continue
                else:
                    #print "Data put"
                    print pd

        print "CYCLE START"

        while (1):
            if not data.empty():
                item = data.get()
            else:
                continue

        return


        #self.start_time = clock()
        #rt_traffic = RepeatedTimer(2,self.refresh_send) # Sending traffic
        #rt_ping = RepeatedTimer(4,self.process_ping) # Sending ping

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
            print "Timer Started"
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

class my_tcpdump(Thread):
    def __init__(self,int,data):
        Thread.__init__(self)
        self.int = int
        self.data = data

    def run(self):
        cmd = "tcpdump -n -nn -l -i " + self.int
        args = shlex.split(cmd)
        # Here STP & ARP calls are not included
        p = re.compile(r'.*IP.(?P<src>[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*)\..*>.'
                       r'(?P<dst>[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*)\..*'
                       r'(length.(?P<len>[0-9]*)|\((?P<len2>[0-9]*)\))$')
        proc = Popen(args, stdout=PIPE, stderr=STDOUT)
        for line in iter(proc.stdout.readline,''):
            pd = self.parse_output(line,p)
            if not pd:
                #print "BAD LINE: " + line
                continue
            else:
                #print "Data put"
                self.data.put(pd)

    def parse_output(self,line,regexp):
        m = regexp.search(line)
        if not m:
            return False
        if m.group('len') == None:
            len = m.group('len2')
        else:
            len = m.group('len')
        return (line, m.group('src'),m.group('dst'),len)


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


client = ClientTraffic("eth0")
client.launch("10.2.0.51",12345)
