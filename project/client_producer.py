import zmq
import time
import sys
# from consistent_hashing import ConsistentHashing
from collections import defaultdict
from itertools import cycle
from hrw import HRWHashing

"""
def create_clients(servers):
    producers = {}
    context = zmq.Context()
    for server in servers:
        print(f"Creating a server connection to {server}...")
        producer_conn = context.socket(zmq.PUSH)
        producer_conn.bind(server)
        producers[server] = producer_conn
    return producers
    
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
def server_1(port=7071):
    context = zmq.Context()
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://127.0.0.1:7071")

    consumer_sender = context.socket(zmq.PUSH)
    consumer_sender.bind("tcp://127.0.0.1:7070")

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
            result = "ADD_RESULT"
        elif "REMOVE" in work:
            result = "REMOVE_RESULT"
        elif "STATS" in work:
            result = "STATS_RESULT"
        else:
            pass
        consumer_sender.send_json(result)
if __name__ == "__main__":
    server_1()
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
    