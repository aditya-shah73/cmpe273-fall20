import zmq
import time
import sys
import consul
from consistent_hashing import ConsistentHashing
from collections import defaultdict
from itertools import cycle
from hrw import HRWHashing

from server_consumer import Server

def create_clients(servers):
    producers = {}
    context = zmq.Context()
    for server in servers:
        print(f"Creating a server connection to {server}...")
        producer_conn = context.socket(zmq.PUSH)
        producer_conn.bind(server)
        producers[server] = producer_conn
    return producers

"""
def generate_data_round_robin(servers):
    producers = create_clients(servers)
    pool = cycle(producers.values())
    print("Starting...")
    for num in range(10):
        data = { 'key': f'key-{num}', 'value': f'value-{num}' }
        print(f"Sending data:{data}")
        next(pool).send_json(data)
    print("Done")


def generate_data_consistent_hashing(servers):
    consistent_hash = ConsistentHashing(servers)
    producers = create_clients(servers)
    result = defaultdict(int)
    print("Starting Consistent Hashing...")
    for num in range(1000):
        data = { 'key': f'key-{num}', 'value': f'value-{num}' }
        print(f"Sending data:{data}")
        server_to_send = consistent_hash.get_server(f'key-{num}')
        print(f"on server : {server_to_send}")
        producers[server_to_send].send_json(data)
        result[server_to_send] += 1
    print(result)
    print("Done")


def generate_data_hrw_hashing(servers):
    hrw_hash = HRWHashing(servers)
    producers = create_clients(servers)
    result = defaultdict(int)
    print("Starting HRW Hashing...")
    for num in range(100000):
        data = { 'key': f'key-{num}', 'value': f'value-{num}' }
        print(f"Sending data:{data}")
        server_to_send = hrw_hash.get_server(f'key-{num}')
        print(f"on server : {server_to_send}")
        producers[server_to_send].send_json(data)
        result[server_to_send] += 1
    print(result)
    print("Done")

"""


def create_baseline(number_of_servers, number_of_keys, consul_obj):
    server_to_obj = {}
    servers = []
    # create servers
    for i in range(number_of_servers):
        try:
            is_registered = consul_obj.agent.service.register(f"baseline-{i}", address="127.0.0.1", port=int(f"300{i}"))
            time.sleep(80 / 1000.0)
            if is_registered:
                print(f"Done registering baseline-{i} to consul!")
                s = Server(name=f"baseline-{i}", address="127.0.0.1", port=f"300{i}")
                s.spawn_server()
                servers.append(s.get_hashable_name())
                server_to_obj[s.get_hashable_name()] = s
            else:
                print("Consul registration Failed!!!")
        except Exception as e:
            print("Something went wrong. Check if your Consul is up!")
    
    producers = create_clients(servers)
    consistent_hashing = ConsistentHashing(servers=servers, server_to_obj=server_to_obj)
    
    result = defaultdict(int)
    for num in range(number_of_keys):
        data = { 'key': f'key-{num}', 'value': f'value-{num}' }
        print(f"Sending data:{data}")
        server_to_send = consistent_hashing.get_server(f'key-{num}')
        print(f"on server : {server_to_send}")
        producers[server_to_send].send_json(data)
        result[server_to_send] += 1
    
    print(result)
    print("hisadsafdsadff")
    return consistent_hashing


def server_producer(port=7071):
    context = zmq.Context()
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://127.0.0.1:7000")

    consumer_sender = context.socket(zmq.PUSH)
    consumer_sender.bind("tcp://127.0.0.1:7001")

    consul_obj = consul.Consul()

    # Create baseline for consistent hashing.
    consistent_hashing = create_baseline(number_of_servers=5, number_of_keys=1000, consul_obj=consul_obj)
    
    # import pdb;pdb.set_trace()
    print("hi")
    # consistent_hashing = ConsistentHashing()
    
    
    # try:
    #     node_data = {'ADD': {'name': 'server-1995', 'address': '127.0.0.1', 'port': '1234'}}
    #     is_registered = consul_obj.agent.service.register(node_data["ADD"]["name"], address=node_data["ADD"]["address"], port=1234)  
    #     if is_registered:
    #         # Spawn the server
    #         # consul_obj.agent.services()
    #         s = Server(name=node_data["ADD"]["name"], address=node_data["ADD"]["address"], port="1234")
    #         s.spawn_server()
    #         # This will redistribute the keys too.
    #         import pdb;pdb.set_trace()
    #         consistent_hashing.add_node(s)
    #         print("DONE ADDING!")
    #     else:
    #         print("Consul registration Failed!!!")
    # except Exception as e:
    #     print("Something went wrong. Check if your Consul is up!")

    # print("Done")

    while True:
        work = consumer_receiver.recv_json()
        print(work)
        if "op" in work and work["op"] == "PUT":
            result = "PUT_RESULT"
        elif "op" in work and work["op"] == "GET_ONE":
            result = "GET_ONE_RESULT"
        elif "op" in work and work["op"] == "GET_ALL":
            result = "GET_ALL_RESULT"
        elif "ADD" in work:
            node_data = work
            # Register node to consul as a service
            try:
                
                is_registered = consul_obj.agent.service.register(node_data["ADD"]["name"], address=node_data["ADD"]["address"], port=int(node_data["ADD"]["port"]))  
                if is_registered:
                    # Spawn the server
                    # consul_obj.agent.services()
                    s = Server(name=node_data["ADD"]["name"], address=node_data["ADD"]["address"], port=node_data["ADD"]["port"])
                    s.spawn_server()
                    print(id(s))
                    import pdb;pdb.set_trace()
                    # This will redistribute the keys too.
                    consistent_hashing.add_node(s)
                    print("DONE ADDING!")
                else:
                    print("Consul registration Failed!!!")
            except Exception as e:
                print("Something went wrong. Check if your Consul is up!")

            result = "ADD_RESULT"
        elif "REMOVE" in work:
            result = "REMOVE_RESULT"
        elif "STATS" in work:
            result = "STATS_RESULT"
        else:
            pass
        consumer_sender.send_json(result)


if __name__ == "__main__":
    server_producer()
    # servers = []
    # num_server = 1
    # if len(sys.argv) > 1:
    #     num_server = int(sys.argv[1])
    #     print(f"num_server={num_server}")
        
    # for each_server in range(num_server):
    #     server_port = "200{}".format(each_server)
    #     servers.append(f'tcp://127.0.0.1:{server_port}')
    
    # print("Servers:", servers)
    # # generate_data_round_robin(servers)
    # generate_data_consistent_hashing(servers)
    # server_1()
    # # generate_data_hrw_hashing(servers)
    
