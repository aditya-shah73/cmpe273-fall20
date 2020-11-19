import math
import sys
from bisect import bisect
import hashlib
import zlib

DEFAULT_REPLICA_FACTOR=40

class ConsistentHashing:

    def __init__(self, nodes=None, replicas=None):
        # Dictionary maintaning mapping between hash and the servers.
        # Ex. 177580411492797401162128409816996889184 -> 'tcp://127.0.0.1:2001'
        self.ring = dict()

        # Utility list for keeping node hashes sorted. 
        # So that we can find the nearest possible server to store value
        self._sorted_keys = []

        # Keeps track of all the nodes in the system
        self.nodes = nodes

        # replicas for the servers ON THE RING
        if not replicas:
            replicas = {}
        self.replicas = replicas

        # Private method which hashes nodes to the ring.
        self._generate_circle()

    def _generate_circle(self):
        for node in self.nodes:
            if node in self.replicas.keys():
                current_replica = self.replicas[node]
            else:
                current_replica = DEFAULT_REPLICA_FACTOR
            for i in range(current_replica):
                key = self._hash_digest('{0}-{1}'.format(node,i))
                self.ring[key] = node
                self._sorted_keys.append(key)
        # import pdb;pdb.set_trace()
        self._sorted_keys.sort()

    def get_node(self, key):
        pos = self.get_node_pos(key)
        if pos is None:
            return None
        # import pdb;pdb.set_trace()
        return self.ring[self._sorted_keys[pos]]

    def get_node_pos(self, string_key):
        """
        """
        if not self.ring:
            return None

        key = self._hash_digest(string_key)

        nodes = self._sorted_keys
        pos = bisect(nodes, key)
        # import pdb;pdb.set_trace()
        if pos == len(nodes):
            return 0
        else:
            return pos

    def _hash_digest(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(),16)
        # return zlib.adler32(str.encode(key)) & 0xffffffff
        # a = hash(str(key).encode())
        # if a < 0:
        #     a = a * -1
        # return a 