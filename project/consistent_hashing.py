"""
Implementation of Consistent Hashing
Reference: https://github.com/Doist/hash_ring/tree/master/hash_ring
"""
import math
import sys
from bisect import bisect
import hashlib
import zlib
import pickle
import zmq
import copy

from collections import defaultdict
from server_consumer import Server

DEFAULT_REPLICA_FACTOR = 40


class ConsistentHashing:

    def __init__(self, servers=None, replicas=None, server_to_obj=None):
        # Dictionary maintaning mapping between hash and the servers.
        # Ex. 177580411492797401162128409816996889184 -> 'tcp://127.0.0.1:2001'
        self.ring = dict()

        # Utility list for keeping node hashes sorted.
        # So that we can find the nearest possible server to store value
        self._sorted_keys = []

        # Keeps track of all the servers in the system
        if not servers:
            self.servers = []
        else:
            self.servers = servers

        if not server_to_obj:
            self.server_to_obj = {}
        else:
            self.server_to_obj = server_to_obj
        
        # Replicas for the servers on the ring
        if not replicas:
            replicas = {}
        self.replicas = replicas

        # Private method which hashes servers to the ring.
        self.__generate_ring()

    def __generate_ring(self):
        for server in self.servers:
            if server in self.replicas.keys():
                current_replica = self.replicas[server]
            else:
                current_replica = DEFAULT_REPLICA_FACTOR
            for i in range(current_replica):
                key = self.__hash_digest('{0}-{1}'.format(server, i))
                self.ring[key] = server
                self._sorted_keys.append(key)
        self._sorted_keys.sort()
    
    def get_stats(self):
        print("**************[STATS]**************")
        print(f"1. Total number of servers {len(self.servers)}")
        print(f"2. Total number of replicas {DEFAULT_REPLICA_FACTOR}")
        print(" DETAILS -----")
        total_keys = 0
        for server, server_path in self.server_to_obj.items():
            with open(server_path, "rb") as fr:
                server_obj = pickle.load(fr)
                print(f" NAME - {server_obj.name} Total keys - {len(server_obj.data_store)}")
                total_keys += len(server_obj.data_store)
        print(f"TOTAL KEYS {total_keys}")
        print("**************[END OF STATS]**************")
        return 1

    def add_node(self, server_obj, replica_factor=None):
        """
            consul_obj = consul.Consul() not the utility obj
            create_clients - Similar to producer
        """
        # Hash server name and add to ring
        if replica_factor:
            current_replica = replica_factor
        else:
            current_replica = DEFAULT_REPLICA_FACTOR

        server_name = server_obj.get_hashable_name()
        self.server_to_obj[server_name] = f"./pickle_data/127.0.0.1:{server_obj.port}"

        self.servers.append(server_name)

        self.replicas[server_name] = current_replica
        for i in range(current_replica):
            key = '{0}-{1}'.format(server_name,i)
            self.ring[self.__hash_digest(key)] = server_name
        
            # Find the clockwise next server
            # Ex.  f"tcp://{address}:{port}"
            next_server_hashable_name = self.get_server(key)
            
            # Get keys on that server
            next_server_path =  self.server_to_obj[next_server_hashable_name]
            next_server_data = None
            with open(next_server_path, "rb") as fp:
                next_server = pickle.load(fp)
                next_server_data = copy.deepcopy(next_server.get_data())
            
            # Remove keys from the server 
            next_server.remove_data()
            # Reflect that in binary
            with open(next_server_path, "wb") as fp:
                next_server = pickle.dump(next_server, fp)
            
            self._sorted_keys.append(self.__hash_digest(key))
            self._sorted_keys.sort()

            # Now that replica is in the ring and we have the hold of the keys from the server 
            # redistribute it 
            if next_server_data:
                for key in next_server_data:
                    value = next_server_data[key]
                    new_server_for_data_key = self.get_server(key)
                    
                    # self.server_to_obj[new_server_for_data_key].add_data(data)
                    server_obj = None
                    # Remove prefix tcp://
                    new_server_for_data_key = new_server_for_data_key[len("tcp://"):]
                
                    with open(f"./pickle_data/{new_server_for_data_key}", "rb") as fr:
                        server_obj = pickle.load(fr)
                        server_obj.add_data({"key":key, "value":value})

                    with open(f"./pickle_data/{new_server_for_data_key}", "wb") as fp:
                        pickle.dump(server_obj, fp)
            else:
                print("Data not present on next server ..passss....")
        return 1

    def remove_node(self, name, address, port):
        # Get replicas of the server
        # Iterate on all the replicas 
        # Redistribute keys -> Find the next available server and add keys to it (Make sure it is not a replica of the given node)
        # Send signal to consul to deregister service 
        # consul_obj.agent.reregister()
        pass

    def get_server(self, key):
        pos = self.__get_server_pos(key)
        if pos is None:
            return None
        return self.ring[self._sorted_keys[pos]]

    def __get_server_pos(self, string_key):
        if not self.ring:
            return None

        key = self.__hash_digest(string_key)
        servers = self._sorted_keys
        pos = bisect(servers, key)
        # If it goes beyond the length of the server, set it to 0
        # Circular implementation 
        if pos == len(servers):
            return 0
        else:
            return pos

    def __hash_digest(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(),16)
        # return zlib.adler32(str.encode(key)) & 0xffffffff
        # a = hash(str(key).encode())
        # if a < 0:
        #     a = a * -1
        # return a 

    def __repr__(self):
        return f"Total number of servers {len(self.servers)}"

# if __name__ == "__main__":
#     consistent_hashing = ConsistentHashing()
#     s = Server(name="Aditya", address="127.0.0.1", port="5000")
#     s.spawn_server()
#     consistent_hashing.add_node(s)