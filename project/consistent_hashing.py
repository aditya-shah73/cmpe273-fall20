"""
Implementation of Consistent Hashing
Reference: https://github.com/Doist/hash_ring/tree/master/hash_ring
"""
import math
import sys
from bisect import bisect
import hashlib
import zlib
import zmq

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

        # # Create Server -> Keys mapping.
        # self.server_to_keys = defaultdict(list)
        # # self.server_to_keys[server].append() 

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

    def add_node(self, server_obj, replica_factor=None):
        """
            consul_obj = consul.Consul() not the utility obj
            create_clients - Similar to producer
        """
        import pdb;pdb.set_trace()
        print(id(server_obj))
        # Hash server name and add to ring
        if replica_factor:
            current_replica = replica_factor
        else:
            current_replica = DEFAULT_REPLICA_FACTOR

        server_name = server_obj.get_hashable_name()
        self.server_to_obj[server_name] = server_obj

        self.replicas[server_name] = current_replica
        for i in range(current_replica):
            key = '{0}-{1}'.format(server_name,i)
            self.ring[self.__hash_digest(key)] = server_name
            self.servers.append(server_name)

            # Find the clockwise next server
            # Ex.  f"tcp://{address}:{port}"
            next_server_hashable_name = self.get_server(key)
            
            # Get keys on that server
            next_server =  self.server_to_obj[next_server_hashable_name]
            next_server_data = next_server.get_data()
            
            # Remove keys from the server 
            next_server.remove_data()

            self._sorted_keys.append(self.__hash_digest(key))
            self._sorted_keys.sort()

            # Now that replica is in the ring and we have the hold of the keys from the server 
            # redistribute it 
            if next_server_data:
                for data in next_server_data:
                    data_key = data["key"]
                    new_server_for_data_key = self.get_server(data_key)
                    self.server_to_obj[new_server_for_data_key].add_data(data)
            else:
                print("Data not present on next server ..passss....")
        return 1

    def remove_node(self, consul_obj, name, address, port):
        # Get replicas of the server
        # Iterate on all the replicas 
        # Redistribute keys -> Find the next available server and add keys to it (Make sure it is not a replica of the given node)
        # Send signal to consul to deregister service 
        consul_obj.agent.reregister()
    
    def redistribute_keys(self, source_server, destination_server):
        # Get the data from the source_server
        # Rehash the entire data
        # Send it to either the source or the destination based on get_server
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