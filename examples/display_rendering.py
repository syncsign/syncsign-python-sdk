import json
import time
from syncsign.client import Client
from syncsign.configuration import Configuration

client = Client(
    api_key='85d34cb6-7f12-4fc4-9813-154e34075615',
)
renderApi = client.display_render

def check(renderId):
    ok = False
    timeout = 600
    while timeout:
        result = renderApi.get_result(renderId)
        if result.is_success():
            data = result.body.get('data')
            if data:
                if data.get('isRendered'):
                    ok = True
                    break
                else:
                    print("awaiting render result...", 600 - timeout)
            else:
                print(json.dumps(result.body, indent=4))
        elif result.is_error():
            print("Error", result.errors)
        timeout -= 10
        time.sleep(10)
    return ok


def send(nodeId, template):
    print('---- render on a display node ----')
    renderId = None
    result = renderApi.one_node_rendering(nodeId, template)
    if result.is_success():
        data = result.body.get('data')
        if data and type(data) is dict:
            renderId = list(data.keys())[0]
            print('Queued, render ID:', renderId)
        else:
            print(json.dumps(result.body, indent=4))
    elif result.is_error():
        print(result.errors)
    return renderId

if __name__ == '__main__':
    template = """
    {
    "background": {},
    "items": [
        {
            "type": "TEXT",
            "data": {
                "font": "YKSZ_BOLD_44",
                "block": { "x": 16, "y": 16, "w": 200, "h": 56 },
                "text": "HELLO"
            }
        }
    ]
    }
    """

    nodeId = '00124B001675CCAE'
    renderId = send(nodeId, template)
    if renderId:
        print('---- check render result ----')
        ok = check(renderId)
        if ok:
            print('Rendering completed.')
        else:
            print('Rendering failed, or timeout.')
