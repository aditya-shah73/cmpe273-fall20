#Spawn a new server -> Selecting a port 
#Register with consul
#difference between consul members and services
#Python continuously run and get input on run 
#Retrieve Data Store Dict on every server (GET, POST)
####To Do########
#Add port number 
#Entry to get request

"""
- A -> B but B->A should not possible on redistribute. Bisect in one direction
- Dynamically add/remove service using API
- Sending signals to consul 
- Node removal/addition is manual
- Create server using Process and register to consul
- Dot in node name error (if occurs)
https://python-consul.readthedocs.io/en/latest/
https://www.programcreek.com/python/example/104783/consul.Consul

How to store data on a consumer to be able to retriev it later?
Add node (Replication factor)
"""

import consul

c = consul.Consul()
index = None
while True:
    index, data = c.kv.get('foo', index=index)
    print data['Value']
