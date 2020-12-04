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
import os
import time 
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
        print("Getting stats.......")
        time.sleep(2)
        for server, server_path in self.server_to_obj.items():
            with open(server_path, "rb") as fr:
                data = fr.read()
                server_obj = pickle.loads(data)
                # server_obj = pickle.load(fr)
                print(f" NAME - {server_obj.name} Total keys - {len(server_obj.data_store)}")
                total_keys += len(server_obj.data_store)
        print(f"TOTAL KEYS {total_keys}")
        print("**************[END OF STATS]**************")
        return 1

    def add_node(self, server_obj, replica_factor=None):
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
                pickle.dump(next_server, fp)
            
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

    def remove_node(self, name, address, port, replica_factor=None):
        
        server_to_be_removed_name = f"tcp://{address}:{port}"

        if replica_factor:
            current_replica = replica_factor
        else:
            current_replica = DEFAULT_REPLICA_FACTOR
        
        # Get the server_obj
        server_to_be_removed_obj = None
        server_to_be_removed_data = None
        server_to_be_removed_path = f"./pickled_data/{server_to_be_removed_name}"
        # Removing the prefix tcp://
        server_to_be_removed_pickled_name = server_to_be_removed_name[len("tcp://"):]
        with open(f"./pickle_data/{server_to_be_removed_pickled_name}", "rb") as fp:
            server_to_be_removed_obj = pickle.load(fp)
            server_to_be_removed_data = copy.deepcopy(server_to_be_removed_obj.get_data())
        
        # Remove from the server list.
        self.servers.remove(server_to_be_removed_name)
        del self.server_to_obj[server_to_be_removed_name]

        # Remove keys from the server 
        server_to_be_removed_obj.remove_data()
        # Reflect that in binary
        with open(f"./pickle_data/{server_to_be_removed_pickled_name}", "wb") as fp:
            pickle.dump(server_to_be_removed_obj, fp)
        
        # Now, remove replicas
        for i in range(current_replica):
            key = '{0}-{1}'.format(server_to_be_removed_name, i)
            key_hash = self.__hash_digest(key)
            del self.ring[key_hash]
            self._sorted_keys.remove(key_hash)
        self._sorted_keys.sort()
        
        if self.replicas and server_to_be_removed_name in self.replicas:
            del self.replicas[server_to_be_removed_name]
        
        # Re-distribute keys
        if server_to_be_removed_data:
            for key, value in server_to_be_removed_data.items():
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
            print("Data not present on current server ..passss....")

        # Remove pickled file from pickle_data
        if os.path.exists(f"./pickle_data/{server_to_be_removed_pickled_name}"):
            os.remove(f"./pickle_data/{server_to_be_removed_pickled_name}")

        return 1

    def put_data(self, data):
        key, value  = data["key"], data["value"]
        server_name = self.get_server(key)
        server_obj = None
        # Removing the prefix tcp://
        server_pickle_name = server_name[len("tcp://"):]
        with open(f"./pickle_data/{server_pickle_name}", "rb") as fp:
            server_obj = pickle.load(fp)
            server_obj.add_data(data)
        # Write it 
        with open(f"./pickle_data/{server_pickle_name}", "wb") as fp:
            pickle.dump(server_obj, fp)
        
        # Make sure it is in the server
        with open(f"./pickle_data/{server_pickle_name}", "rb") as fp:
            server_obj = pickle.load(fp)
            assert key in server_obj.data_store 
        return 1
    
    def get_data_by_key(self, key):
        server_name = self.get_server(key)
        server_obj = None
        ret = {}
        ret["key"] = key
        # Removing the prefix tcp://
        server_pickle_name = server_name[len("tcp://"):]
        with open(f"./pickle_data/{server_pickle_name}", "rb") as fp:
            server_obj = pickle.load(fp)
            ret["value"] = server_obj.get_data_by_key(key)
        assert "value" in ret
        assert "key" in ret
        return ret 
    
    def get_all_keys_by_server(self, address, port, name=None):
        server_pickle_name = f"{address}:{port}"
        server_obj = None
        ret = []
        with open(f"./pickle_data/{server_pickle_name}", "rb") as fp:
            server_obj = pickle.load(fp)
            response_from_server = server_obj.get_data()
            temp_dict = {}
            for key, value in response_from_server.items():
                temp_dict["key"], temp_dict["value"] = key, value
                ret.append(copy.deepcopy(temp_dict))
                temp_dict.clear()
        return ret
                
    def get_all_keys(self):
        ret = {}
        collection = []
        for server in self.servers:
            server_pickle_name = server[len("tcp://"):]
            address, port = server_pickle_name.split(":")
            assert address == "127.0.0.1"
            collection.extend(self.get_all_keys_by_server(address, port))
        ret["collection"] = collection
        return ret

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
        # a = hash(str(key).encode())
        # if a < 0:
        #     a = a * -1
        # return a 

    def __repr__(self):
        return f"Total number of servers {len(self.servers)}"
