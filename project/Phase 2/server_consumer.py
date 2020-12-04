import zmq
import sys
import pickle
from  multiprocessing import Process

class Server:
    def __init__(self, name, address, port):
        self.name , self.address, self.port = name, address, port
        self.data_store = {}

    def run(self):
        context = zmq.Context()
        consumer = context.socket(zmq.PULL)
        consumer.connect(f"tcp://127.0.0.1:{self.port}")
        
        while True:
            raw = consumer.recv_json()
            key, value = raw['key'], raw['value']
            # print(f"Server_port={self.port}:key={key},value={value}")
            # Deserialize 
            server_obj = None
            with open(f"./pickle_data/127.0.0.1:{self.port}", "rb") as fr:
                data = fr.read()
                server_obj = pickle.loads(data)
                server_obj.data_store[key] = value
            
            with open(f"./pickle_data/127.0.0.1:{self.port}", "wb") as fp:
                pickle.dump(server_obj, fp)
                
    def terminate(self):
        self.process.terminate()

    def spawn_server(self):
        self.process = Process(target=self.run)
        self.process.start()
    
    def get_data(self):
        return self.data_store
    
    def get_data_by_key(self, key):
        return self.data_store[key]
    
    def get_hashable_name(self):
        return f"tcp://{self.address}:{self.port}"

    def remove_data(self):
        self.data_store.clear()
    
    def add_data(self, data):
        self.data_store[data["key"]] = data["value"]