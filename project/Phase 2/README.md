## Phase 2

In the phase 2, you will be adding retrieval GET by Id/key and GET all operations in both client and server sides. In addtion, the PUT method will get modified to work with new interface.

## Steps to run Phase 2

Results for 5,000 , 10,000 , 50,000 and 100,000 key distribution can be found under the results folder

```
pipenv shell
pipenv install
```

Install consul and start a consul agent on one terminal
```
consul agent -dev -enable-script-checks
```
Start the client middleware on another terminal
```
python client_middleware.py
```

Start the client on another terminal
```
python client_producer.py
```

To add more operations edit the operations.txt file


### PUT

_JSON Request Payload_

```json
{
    "op": "PUT",
    "key": "key",
    "value": "value"
}
```


### GET by key

_JSON Request Payload_

```json
{
    "op": "GET_ONE",
    "key": "key"
}
```

_JSON Response Payload_

```json
{
    "key": "key",
    "value": "value"
}
```

### GET All

_JSON Request Payload_

```json
{
    "op": "GET_ALL",
}
```

_JSON Response Payload_

```json
{
    "collection": [
        {
            "key": "key1",
            "value": "value1"
        },
        {
            "key": "key2",
            "value": "value2"
        }
    ]
}
```

### Cluster Membership

In order to dynamically control the node membership, your system will integrate with [Consul](https://www.consul.io/).

In the phase 1, we collected cluster size from the command line and mapped to nodes using this scheme of 

```python
server_port = "200{}".format(each_server)
```

In the phase 2, both client and server will no longer read the initial cluster size from the command line. Instead, you will be 
loading from Consul.

First, each node will be registered to the membership in Consul during the server boot up. Upon the server shut down, the node will be 
removed from the membership.

Similarly on the client side, you will first lookup the membership from Consul and then the data will be sharded across different nodes.

### Cluster Adjustment

Adding and removing nodes will be supported in the consistent hashing mode only and node rebalancing--moving data from one node to another--will 
be handled on the client side by sending the _remove_ and _add_ signals to Consul. 

_Steps to remove node_

- Pick a node to be removed.
- Re-balance data to the other nodes.
- After removal is done, send _remove_ signal to Consul.

_Steps to add node_

- Send _add_ signal to Consul.
- Server will get a push notification about the membership changes.
- Launch a new server process based on the node information given by Consul.
- Re-balance existing data to the new node.
