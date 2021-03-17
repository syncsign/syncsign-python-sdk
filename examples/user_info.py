import json
from syncsign.client import Client
from syncsign.configuration import Configuration


client = Client(
    api_key='85d34cb6-7f12-4fc4-9813-154e34075615',
)

userApi = client.user

print('---- get user info ----')
result = userApi.info()
if result.is_success():
    print(json.dumps(result.body, indent=4))
elif result.is_error():
    print(result.errors)
