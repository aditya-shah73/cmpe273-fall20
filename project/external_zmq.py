# Read from json file.
# Send the operations from JSON to producer wala ZMQ 
# Get response from ZMQ 1 for okay operations
# If 1, then move to next operation.

import zmq
import sys
import json
from  multiprocessing import Process

PRODUCER_ZMQ_PORT = "7071"
ENTRY_CLIENT_PORT = "7070"
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
        # Read operations.
        if idx == 0:
            idx += 1
            with open("./data/operations1.txt", "r") as fp: #TODO Hardcode.
                for json_obj in json.load(fp):
                    print(f"Sending operation -> {json_obj}")
                    client_sender.send_json(json_obj)
        
                    # Receive the response.
                    work = client_receiver.recv_json()
                    print(f"Got response {work}")

if __name__ == '__main__':
    server()