import zmq
import time
import sys
from itertools import cycle
from consistent_hashing import ConsistentHashing

def create_clients(servers):
    producers = {}
    context = zmq.Context()
    for server in servers:
        print(f"Creating a server connection to {server}...")
        producer_conn = context.socket(zmq.PUSH)
        producer_conn.bind(server)
        producers[server] = producer_conn
    # import pdb; pdb.set_trace()
    return producers
    

def generate_data_round_robin(servers):
    print("Starting...")
    producers = create_clients(servers)
    pool = cycle(producers.values())
    for num in range(10):
        data = { 'key': f'key-{num}', 'value': f'value-{num}' }
        print(f"Sending data:{data}")
        next(pool).send_json(data)
        # time.sleep(1)
    print("Done")


def generate_data_consistent_hashing(servers):
    consistent_hash = ConsistentHashing(servers)
    print("Starting...")
    producers = create_clients(servers)
    from collections import defaultdict
    result = defaultdict(int)
    for num in range(1000):
        data = { 'key': f'key-{num}', 'value': f'value-{num}' }
        print(f"Sending data:{data}")
        server_to_send = consistent_hash.get_node(f'key-{num}')
        print(f"on server : {server_to_send}")
        producers[server_to_send].send_json(data)
        result[server_to_send] += 1
        # time.sleep(0.1)
    print(result)
    print("Done")

def generate_data_hrw_hashing(servers):
    print("Starting...")
    ## TODO
    print("Done")
    
    
if __name__ == "__main__":
    servers = []
    num_server = 1
    if len(sys.argv) > 1:
        num_server = int(sys.argv[1])
        print(f"num_server={num_server}")
        
    for each_server in range(num_server):
        server_port = "200{}".format(each_server)
        servers.append(f'tcp://127.0.0.1:{server_port}')
    

    print("Servers:", servers)
    # generate_data_round_robin(servers)
    generate_data_consistent_hashing(servers)
    # generate_data_hrw_hashing(servers)
    
