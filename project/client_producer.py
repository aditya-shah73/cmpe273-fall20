import zmq
import time
import sys
import consul
import pickle
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


def create_baseline(number_of_servers, number_of_keys, consul_obj):    
    server_to_obj = {}
    servers = []
    # create servers
    for i in range(number_of_servers):
        try:
            is_registered = consul_obj.agent.service.register(f"baseline-{i}", address="127.0.0.1", port=int(f"300{i}"))
            time.sleep(80 / 1000.0)
            if is_registered:
                print(f"[IN create_baseline] Done registering baseline-{i} to consul!")
                s = Server(name=f"baseline-{i}", address="127.0.0.1", port=f"300{i}")
                # Pickle it 
                with open(f"./pickle_data/127.0.0.1:300{i}", "wb") as fp:
                    pickle.dump(s, fp)
                s.spawn_server()
                servers.append(s.get_hashable_name())
                server_to_obj[s.get_hashable_name()] = f"./pickle_data/127.0.0.1:300{i}"
            else:
                print("[IN create_baseline] Consul registration Failed!!!")
        except Exception as e:
            print("[IN create_baseline] Something went wrong.")
    
    consistent_hashing = ConsistentHashing(servers=servers, server_to_obj=server_to_obj)
    
    producers = create_clients(servers)

    result = defaultdict(int)
    for num in range(number_of_keys):
        data = { 'key': f'key-{num}', 'value': f'value-{num}' }
        server_to_send = consistent_hashing.get_server(f'key-{num}')
        print(f"[IN create_baseline] Sending data:{data} on server : {server_to_send}")
        producers[server_to_send].send_json(data)
        result[server_to_send] += 1
    
    print(f"[IN create_baseline] STARTING STATS {result}")
    return consistent_hashing


def server_producer(port=7071):
    context = zmq.Context()
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://127.0.0.1:7000")

    consumer_sender = context.socket(zmq.PUSH)
    consumer_sender.bind("tcp://127.0.0.1:7001")

    consul_obj = consul.Consul()

    # Create baseline for consistent hashing.
    consistent_hashing = create_baseline(number_of_servers=5, number_of_keys=100, consul_obj=consul_obj)
    #consistent_hashing = ConsistentHashing()
    time.sleep(2)
    while True:
        work = consumer_receiver.recv_json()
        print(f"[server_producer] current operation {work}")
        # time.sleep(2)
        if "op" in work and work["op"] == "PUT":
            assert "key" in work
            assert "value" in work
            result = consistent_hashing.put_data({"key":work["key"], "value":work["value"]})
        elif "op" in work and work["op"] == "GET_ONE":
            assert "key" in work
            result = consistent_hashing.get_data_by_key(key=work["key"])
        elif "op" in work and work["op"] == "GET_ALL":
            if len(work) == 1:
                result = consistent_hashing.get_all_keys()
            else:
                assert "name" in work
                assert "address" in work
                assert "port" in work

                name, address, port = work["name"], work["address"], work["port"]
                result = consistent_hashing.get_all_keys_by_server(address=address, port=port, name=name)
            
        elif "op" in work and work["op"] == "STATS":
            result=consistent_hashing.get_stats()
        elif "ADD" in work:
            node_data = work
            try:
                 # Register node to consul as a service
                is_registered = consul_obj.agent.service.register(node_data["ADD"]["name"], address=node_data["ADD"]["address"], port=int(node_data["ADD"]["port"]))  
                time.sleep(40 / 1000.0)
                if is_registered:
                    # Spawn the server
                    # consul_obj.agent.services()
                    s = Server(name=node_data["ADD"]["name"], address=node_data["ADD"]["address"], port=node_data["ADD"]["port"])
                    
                    # Pickle it 
                    with open(f"./pickle_data/127.0.0.1:{node_data['ADD']['port']}", "wb") as fp:
                        pickle.dump(s, fp)
                
                    s.spawn_server()
                    # Adding node in the ring
                    result = consistent_hashing.add_node(s)
                    print("[server_producer] DONE ADDING!")
                else:
                    print("[server_producer] Consul registration Failed!!!")
            except Exception as e:
                print("[server_producer][ADD] Something went wrong.")
        elif "REMOVE" in work:
            node_data = work
            name = node_data["REMOVE"]["name"]
            address = node_data["REMOVE"]["address"]
            port = node_data["REMOVE"]["port"]
            try:
                # De-register node from consul
                is_deregistered = consul_obj.agent.service.deregister(name)
                time.sleep(80 / 1000.0)
                if is_deregistered:
                    # Remove the node from the ring and re-distribute the keys.        
                    result = consistent_hashing.remove_node(name, address, port)
                else:
                    print("[server_producer][REMOVE] Consul de-registration Failed!!!")
            except Exception as e:
                print("[server_producer][REMOVE] Something went wrong.")         
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
    
