"""
Implementation of HRW Hashing
"""
import sys
import hashlib
import zlib

class HRWHashing:
    def __init__(self, servers=None):
        # Keeps track of all the nodes in the system
        self.servers=servers

    def __hash_digest(self, key, server):
        hash = hashlib.md5()
        hash.update(key)
        hash.update(server)
        return int(hash.hexdigest(), 16)

    def get_server(self, key):
        highest_weight = 0
        selected_server = None
        for server in self.servers:
            weight = self.__hash_digest(key.encode() , server.encode())
            if weight > highest_weight:
                highest_weight = weight
                selected_server = server
        return selected_server
