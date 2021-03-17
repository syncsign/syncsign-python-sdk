import json
from syncsign.client import Client
from syncsign.configuration import Configuration


client = Client(
    api_key='85d34cb6-7f12-4fc4-9813-154e34075615',
)

nodeApi = client.nodes

print('---- list all nodes ----')
result = nodeApi.list_nodes()
if result.is_success():
    print(json.dumps(result.body, indent=4))
elif result.is_error():
    print(result.errors)

print('---- get one node ----')
if result.body.get('data'):
    nodeId = result.body.get('data')[0].get('nodeId')
    result = nodeApi.get_node(nodeId)
    if result.is_success():
        print(json.dumps(result.body, indent=4))
    elif result.is_error():
        print(result.errors)
