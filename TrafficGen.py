__author__ = 'ash'

import random
import time


class TrafficGen:

    def __init__(self, node_list, bwhist):
        self.node_list = node_list
        #self.start = time.clock()
        self.traffic = dict()
        self.bw_hist = bwhist
        self.bw_refresh = 2
        self.bw_id = 0 # this field is required for recording simultaneous channel usage

    def generator(self):
        """
        Generating traffic - packets width dst, src and len
        Every 2 seconds dumps the aggregated info to calculate the bandwidth
        """
        self.start = time.clock()
        worktime = time.clock()
        while True:
            if time.clock() - worktime > 10: # for tests. Get stat for 10 seconds
                break;
            rand = random.randint(0,5000) # there is a chance for packet to appear
            if rand == 0:
                capt_time = time.clock()
                if capt_time - self.start > self.bw_refresh: # as the refresh time elapsed
                    self.process_bandwidth(capt_time) # we calculate the bandwidth for this period
                    self.bw_id += 1 # next will be sniffed traffic for new period
                    self.start = capt_time # reset the start time
                    self.traffic.clear() # clear the current traffic information container
                (src,dst) = self.example_load()
                if src == dst: # if src and dst are equal - we inc with mod
                    dst += 1
                    dst % len(self.node_list)
                length = random.randint(500,1500)
                pk = Packet(src,dst,length)
                if (src,dst) not in self.traffic:
                    self.traffic[(src,dst)] = 0
                self.traffic[(src,dst)] += length # accumulate the length of packets in our history dict


    def process_bandwidth(self,capt_time):
        #os.system('clear')
        print "Bandwidth refresh " + str(self.bw_refresh) + " seconds"
        for k in self.traffic.keys():
            bandwidth = self.traffic[k] / (capt_time - self.start) # simple bandwidth calculate formula. capt_time is the last time record in this period
            (src,dst) = k
            self.bw_hist.append((src,dst),bandwidth,self.bw_id) # Give command to append the traffic info
            #sys.stdout.write(str(src) + " > " + str(dst) + "\t\t" + str(bandwidth) + "\n")

    def example_load(self):
        """
        9 to 3 - heavy
        8 to 10 - heavy
        0 to * - low
        """
        nodelen = len(self.node_list)
        rand = random.randint(0,nodelen*3)
        if rand > 2*nodelen:
            (src,dst) = (9,3)
        elif rand <= 2*nodelen and rand >= nodelen:
            (src,dst) = (8,10)
        else:
            (src,dst) = (0,random.randint(0,nodelen-1))
        return (src,dst)

class Packet:
    """
    Class describes the packet info
    """

    def __init__(self, src, dst, length):
        self.src = src
        self.dst = dst
        self.len = length