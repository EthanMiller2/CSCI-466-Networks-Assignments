'''
Created on Oct 12, 2016

@author: mwittie
'''
import network_4
import link_4
import threading
from time import sleep

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 1 #give the network sufficient time to transfer all packets before quitting
routeA = {1: 0, 2: 1, 3: 2, 4: 3}
routeB = {1: 0, 3: 1}
routeC = {2: 0, 4: 1}
routeD = {1: 0, 2: 1, 3: 2, 4: 3}

# routeA = {0: 3, 1: 4}
# routeB = {0: 3}
# routeC = {0: 4}
# routeD = {0: 3, 1: 4}

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads
    
    #create network nodes
    # create clients and server Host objects and add them to a list of objects
    client1 = network_4.Host(1)
    object_L.append(client1)
    client2 = network_4.Host(2)
    object_L.append(client2)
    server1 = network_4.Host(3)
    object_L.append(server1)
    server2 = network_4.Host(4)
    object_L.append(server2)
    # create the Router objects 
    router_a = network_4.Router(name='A', intf_count=4, max_queue_size=router_queue_size, routingTable = routeA)
    router_b = network_4.Router(name='B', intf_count=2, max_queue_size=router_queue_size, routingTable = routeB)
    router_c = network_4.Router(name='C', intf_count=2, max_queue_size=router_queue_size, routingTable = routeC)
    router_d = network_4.Router(name='D', intf_count=4, max_queue_size=router_queue_size, routingTable = routeD)
    object_L.append(router_a)
    object_L.append(router_b)
    object_L.append(router_c)
    object_L.append(router_d)
    
    #create a Link Layer to keep track of links between network nodes
    link_layer = link_4.LinkLayer()
    object_L.append(link_layer)
    
    #add all the links
    #link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu

    # link between client1 and router_a
    link_layer.add_link(link_4.Link(client1, 0, router_a, 0, 50)) 
    link_layer.add_link(link_4.Link(router_a, 0, client1, 0, 50))
    # link between client2 and router_a
    link_layer.add_link(link_4.Link(client2, 0, router_a, 1, 50))
    link_layer.add_link(link_4.Link(router_a, 1, client2, 0, 50))

    # link between router_a & router_b, router_c
    link_layer.add_link(link_4.Link(router_a, 2, router_b, 0, 50))
    link_layer.add_link(link_4.Link(router_b, 0, router_a, 2, 50))
    link_layer.add_link(link_4.Link(router_a, 3, router_c, 0, 50))
    link_layer.add_link(link_4.Link(router_c, 0, router_a, 3, 50))

    # link between router_d $ router_b, router_c
    link_layer.add_link(link_4.Link(router_d, 0, router_b, 1, 50))
    link_layer.add_link(link_4.Link(router_b, 1, router_d, 0, 50))
    link_layer.add_link(link_4.Link(router_d, 1, router_c, 1, 50))
    link_layer.add_link(link_4.Link(router_c, 1, router_d, 1, 50))

    # link between server1 and router_d
    link_layer.add_link(link_4.Link(router_d, 2, server1, 0, 50))
    link_layer.add_link(link_4.Link(server1, 0, router_d, 2, 50))
    # link between server2 and router_d
    link_layer.add_link(link_4.Link(server2, 0, router_d, 3, 50))
    link_layer.add_link(link_4.Link(router_d, 3, server2, 0, 50))
    

    #start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=client1.__str__(), target=client1.run))
    thread_L.append(threading.Thread(name=server1.__str__(), target=server1.run))
    thread_L.append(threading.Thread(name=client2.__str__(), target=client2.run))
    thread_L.append(threading.Thread(name=server2.__str__(), target=server2.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    thread_L.append(threading.Thread(name=router_b.__str__(), target=router_b.run))
    thread_L.append(threading.Thread(name=router_c.__str__(), target=router_c.run))
    thread_L.append(threading.Thread(name=router_d.__str__(), target=router_d.run))
    
    thread_L.append(threading.Thread(name="Network", target=link_layer.run))
    
    for t in thread_L:
        t.start()
    
        #data that is 80 char long
    server1.udt_send(1, '||||||||||||||||||||||||||||||||||||||||////////////////////////////////////////')
    server2.udt_send(2, '****************************************----------------------------------------')
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)
    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")



# writes to host periodically