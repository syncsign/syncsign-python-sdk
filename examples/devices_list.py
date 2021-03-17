import json
from syncsign.client import Client
from syncsign.configuration import Configuration


client = Client(
    api_key='85d34cb6-7f12-4fc4-9813-154e34075615',
)

devApi = client.devices

print('---- list all devices ----')
result = devApi.list_devices()
if result.is_success():
    print(json.dumps(result.body, indent=4))
elif result.is_error():
    print(result.errors)

print('---- get one device ----')
if result.body.get('data'):
    sn = result.body.get('data')[0].get('thingName')
    result = devApi.get_device(sn)
    if result.is_success():
        print(json.dumps(result.body, indent=4))
    elif result.is_error():
        print(result.errors)
