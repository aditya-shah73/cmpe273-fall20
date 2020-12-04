import zmq
import sys
import json
from  multiprocessing import Process

ENTRY_CLIENT_PORT = "7001"
PRODUCER_ZMQ_PORT = "7000"
def server(port=ENTRY_CLIENT_PORT):
    entry_context = zmq.Context()

    # Read from here.
    client_receiver = entry_context.socket(zmq.PULL)
    client_receiver.connect(f"tcp://127.0.0.1:{ENTRY_CLIENT_PORT}")

    # Push to here
    client_sender = entry_context.socket(zmq.PUSH)
    client_sender.bind(f"tcp://127.0.0.1:{PRODUCER_ZMQ_PORT}")
    
    operations = []
    idx = 0
    while True:
        
        if idx == 0:
            idx += 1
            
            client_sender.send_json({"op":"STATS"})
            work = client_receiver.recv_json()
            print(f"Got response {work}")
            number_of_keys = 2000
            for num in range(number_of_keys):
                str = {'op': 'PUT', 'key': f'key-{num}', 'value': f'value-{num}'}
                print(f"Sending operation -> {str}")
                # print(f"{num}")
                client_sender.send_json(str)
                work = client_receiver.recv_json()
                # print(f"Got response {work}")

            with open("./data/operations.txt", "r") as fp:
                for json_obj in json.load(fp):
                    print(f"Sending operation -> {json_obj}")
                    client_sender.send_json(json_obj)
        
                    # Receive the response.
                    work = client_receiver.recv_json()
                    print(f"Got response {work}")

if __name__ == '__main__':
    server()