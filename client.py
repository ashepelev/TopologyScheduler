__author__ = 'ash'

import socket
from struct import *
import datetime
import pcapy
import sys

def eth_addr (a) :
    b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]), ord(a[4]) , ord(a[5]))
    return b

#function to parse a packet
def parse_packet(packet) :

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
                if data.startswith("192.168.0.101"): # if it is our traffic stat packets
                    res = False

    #print 'Version : ' + str(version) + ' IP Header Length : ' + str(ihl) + ' TTL : ' + str(ttl) + ' Protocol : ' + str(protocol) + ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr)
    #print ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr) + ' Length : ' + str(len(packet))
            return (s_addr,d_addr,len(packet),res)
    return (0,0,0,False)



hostname ="192.168.0.101"
port = 12345
#ipaddr = socket.gethostbyname(hostname)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((hostname, port))


devices = pcapy.findalldevs()
for d in devices:
    print d

print
# Arguments here are:
    #   device
    #   snaplen (maximum number of bytes to capture _per_packet_)
    #   promiscious mode (1 for true)
    #   timeout (in milliseconds)
cap = pcapy.open_live("eth0",65536,1,0)

while (1) :
    (header, packet) = cap.next()
    (src,dst,leng,res) = parse_packet(packet)
    if not res:
       continue
    msg = str(src) + '|' + str(dst) + '|' + str(leng) + ','
#    print "Sending: " + msg
    #s.sendall(bytes(msg,'utf8'))
    s.sendall(msg)

s.close()
