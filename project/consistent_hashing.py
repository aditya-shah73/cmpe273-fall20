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

DEFAULT_REPLICA_FACTOR = 20


class ConsistentHashing:

    def __init__(self, servers=None, replicas=None):
        # Dictionary maintaning mapping between hash and the servers.
        # Ex. 177580411492797401162128409816996889184 -> 'tcp://127.0.0.1:2001'
        self.ring = dict()

        # Utility list for keeping node hashes sorted.
        # So that we can find the nearest possible server to store value
        self._sorted_keys = []

        # Keeps track of all the servers in the system
        self.servers = servers

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

    def add_node(self, consul_obj, zmq_context, name, address, port, consul_check=None, replica_factor=None):
        """
            consul_obj = consul.Consul() not the utility obj
            create_clients - Similar to producer
        """
        # Spawnning a server
        server = f'tcp://{address}:{port}'
        producer_conn = zmq_context.socket(zmq.PUSH)
        producer_conn.bind(server)
        # Registering with consul
        consul_obj.agent.service.register(
            name, address=address, port=port)  # Add consul_check
        # Hash server name and add to ring
        if replica_factor:
            current_replica = replica_factor
        else:
            current_replica = DEFAULT_REPLICA_FACTOR

        self.replicas[server] = current_replica
        for i in range(current_replica):
            key = self.__hash_digest('{0}-{1}'.format(server,i))
            self.ring[key] = server
            #To do: Based on the next server. If next replica is the same server then skip
            self._sorted_keys.append(key)
            self._sorted_keys.sort()
        return None

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
