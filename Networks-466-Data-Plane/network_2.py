'''
Created on Oct 12, 2016

@author: mwittie
'''
import queue
import threading


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize);
        self.mtu = None
    
    ##get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None
        
    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)
        
        
## Implements a network layer packet (different from the RDT packet 
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths 
    dst_addr_S_length = 5
    flagLength = 1 # lengths of flag for packet segmentaion 
    offsetLength = 2 # lenght of offset for packet segmentation
    headerLength = offsetLength + flagLength + dst_addr_S_length # lenght of the header is the aggrigation of the lenghts of offset, flag and dest addy 
    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, dst_addr, data_S, flag=0, offset = 0):
        self.dst_addr = dst_addr
        self.data_S = data_S
        self.flag = flag
        self.offset = offset
        
    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()
        
    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length) # pads addy with zeros on left
        if(self.flag != 0): # if flag is set then execute 
            byte_S += str(self.flag).zfill(self.flagLength) # pads flag with zeros on left
            byte_S += str(self.offset).zfill(self.offsetLength) # pads offset with zeros on left
        byte_S += self.data_S
        return byte_S
    
    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S, mtu):
        dst_addr = int(byte_S[0 : NetworkPacket.dst_addr_S_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length : ]
        segments = []
        segmented = 0
        pointer = 0
        if(NetworkPacket.flagLength + NetworkPacket.offsetLength + len(data_S[pointer:]) > mtu): # checks if we need to segment a packet
            segmented = 1 # set segment flag to true
            while(len(data_S[pointer:]) != 0):
                if(len(data_S[pointer:])+NetworkPacket.flagLength + NetworkPacket.offsetLength == mtu or NetworkPacket.flagLength+NetworkPacket.offsetLength + len(data_S[pointer:]) < mtu): #execute if we no longer need to segement packets
                    segmented = 0 # set segment flag to false
                quavo = pointer + mtu - self.flagLength - self.offsetLength # moves the fragment pointer and assigns it to the next greatest migo (whip it up)
                segments.append(self(dst_addr, data_S[pointer:quavo], segmented, pointer)) # create and append new packet with data from between pointer and quavo offsets
                pointer = quavo #Increse pointer possition to quavo 
            return segments
        else: # if packet does not need to be segmented 
            return self(dst_addr, data_S)


    

    

## Implements a network host for receiving and transmitting data
class Host:
    segments = []

    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False #for thread termination
    
    ## called when printing the object
    def __str__(self):
        return 'Host_%s' % (self.addr)
       
    ## create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, data_S):
        if(len(data_S)+5>self.out_intf_L[0].mtu): #if the lenght of the data string is > the MTU then it needs to be segmented 
            data_S_1 = data_S[0:40] #substring of the first 40 char
            data_S_2 = data_S[41:] # substring of the last 40 char
            p1 = NetworkPacket(dst_addr, data_S_1) # create packet 1 using the first 40 char
            self.out_intf_L[0].put(p1.to_byte_S()) #send packets always enqueued successfully
            print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p1, self.out_intf_L[0].mtu))
            p2 = NetworkPacket(dst_addr, data_S_2) # create packet 2 using the last 40 char
            self.out_intf_L[0].put(p2.to_byte_S()) #send packets always enqueued successfully
            print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p2, self.out_intf_L[0].mtu))
        else: # if the lenght of the data string !> the MTU
            p = NetworkPacket(dst_addr, data_S)
            self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully
            print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))
        
    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()
        if pkt_S is not None: 
            if(pkt_S[NetworkPacket.dst_addr_S_length] == '1'): #if the packet is segmented 
                self.segments.append(pkt_S[NetworkPacket.dst_addr_S_length + NetworkPacket.flagLength + NetworkPacket.offsetLength:]) # append segmented packet to list of segments
            else: # default behavior
                self.segments.append(pkt_S[NetworkPacket.dst_addr_S_length:])
                print('%s: received packet "%s" on the in interface' % (self, pkt_S))
                del self.segments[:] # empty list of segments

    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return
        


## Implements a multi-interface router described in class
class Router:
    
    ##@param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces 
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size):
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    ## called when printing the object
    def __str__(self):
        return 'Router_%s' % (self.name)

    ## look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self):
        self.out_intf_L[0].mtu = 30 # set mtu of out interface to 30 
        for i in range(len(self.in_intf_L)): # for each of the packets in the router queue 
            pkt_S = None
            try:
                #get packet from interface i
                pkt_S = self.in_intf_L[i].get()
                #if packet exists make a forwarding decision
                if pkt_S is not None:
                    p = NetworkPacket.from_byte_S(pkt_S, self.out_intf_L[0].mtu) #parse a packet out
                    # HERE you will need to implement a lookup into the 
                    # forwarding table to find the appropriate outgoing interface
                    # for now we assume the outgoing interface is also i
                    for j in p: # for each segmented packet convert from bytes to string 
                        self.out_intf_L[i].put(j.to_byte_S(), True)
                        print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                        % (self, j.to_byte_S(), i, i, self.out_intf_L[0].mtu))
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass
                
    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return 
