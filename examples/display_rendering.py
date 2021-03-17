import json
import time
from syncsign.client import Client
from syncsign.configuration import Configuration


client = Client(
    api_key='85d34cb6-7f12-4fc4-9813-154e34075615',
)

nodeId = '00124B001675CCAE'
template = """
{
  "background": {},
  "items": [
    {
      "type": "TEXT",
      "data": {
        "font": "YKSZ_BOLD_44",
        "block": { "x": 88, "y": 90, "w": 304, "h": 56 },
        "text": "HELLO"
      }
    }
  ]
}
"""

renderApi = client.display_render
print('---- render on a display node ----')
renderId = None
result = renderApi.one_node_rendering(nodeId, template)
if result.is_success():
    # print(json.dumps(result.body, indent=4))
    data = result.body.get('data')
    if data and type(data) is dict:
        renderId = list(data.keys())[0]
        print('render ID:', renderId)
elif result.is_error():
    print(result.errors)

if renderId:
    print('---- check render result ----')
    ok = False
    timeout = 600
    while timeout:
        timeout -= 10
        result = renderApi.get_result(renderId)
        if result.is_success():
            # print(json.dumps(result.body, indent=4))
            data = result.body.get('data')
            if data:
                if data.get('isRendered'):
                    ok = True
                    break
        elif result.is_error():
            print(result.errors)
        time.sleep(10)
    if ok:
        print('Rendering completed.')
    else:
        print('Rendering failed.')
