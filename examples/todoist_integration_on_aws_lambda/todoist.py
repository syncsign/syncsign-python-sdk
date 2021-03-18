import json
import copy
from datetime import datetime
import requests
from syncsign.client import Client
from syncsign.configuration import Configuration

# See https://todoist.com/prefs/integrations
TODOIST_TOKEN = "0123456789abcdef01234567890123456789abcdef"
# See API Key in https://portal.sync-sign.com/#/setting
SYNCSIGN_TOKEN = '85d34cb6-7f12-4fc4-9813-154e34075615'
# The Display Node which you want to show the todolist
SYNCSIGN_NODE_ID = '00124B001675CCAE'

def fetchTodoList():
    # Request a list from data source: Todoist
    try:
        todos = requests.get(
            "https://api.todoist.com/rest/v1/tasks",
            params={
                "filter": "(today | overdue)"
            },
            headers={
                "Authorization": "Bearer %s" % TODOIST_TOKEN
            }).json()
        # print(json.dumps(todos, indent=4))
        print("Got %d todos" % len(todos))
        return todos
    except Exception as e:
        print('Fetch todoist failed:', e)

def buildLayoutDocument(todos):
    # Build a JSON based on the todo list data
    tpl = {
        "background": {},
        "items": [
            {
                "type": "TEXT",
                "data": {
                    "font": "DDIN_64",
                    "block": { "x": 8, "y": 0, "w": 392, "h": 70 },
                    "text": "Today's Todo"
                }
            },
            {
                "type": "TEXT",
                "data": {
                    "font": "DDIN_32",
                    "block": { "x": 8, "y": 70, "w": 392, "h": 36 },
                    "text": ""
                }
            }
        ]
    }
    ITEM_TPL = {
                "type": "TEXT",
                "data": {
                        "font": "DDIN_CONDENSED_32",
                        "block": { "x": 8, "y": 110, "w": 392, "h": 36 },
                        "text": ""
                    }
                }
    tpl['items'][1]['data']['text'] = datetime.now().strftime("%m/%d/%Y %H:%M")
    posY = 110
    for item in todos:
        x = copy.deepcopy(ITEM_TPL)
        x['data']['block']['y'] = posY
        x['data']['text'] = '- ' + item.get('content')
        tpl['items'].append(x)
        posY += 36
    # print(json.dumps(tpl, indent=4))
    return tpl

def showOnSyncSign(layoutDocument):
    # Add the layout document to the node's refresh queue
    print('Rendering on display node: %s' % SYNCSIGN_NODE_ID)
    renderId = None
    client = Client(api_key = SYNCSIGN_TOKEN)
    result = client.display_render.one_node_rendering(SYNCSIGN_NODE_ID,
                                            json.dumps(layoutDocument))
    if result.is_success():
        # print(json.dumps(result.body, indent=4))
        data = result.body.get('data')
        if data and type(data) is dict:
            renderId = list(data.keys())[0]
            print('Render ID:', renderId)
            return True
    elif result.is_error():
        print(result.errors)
    return False


if __name__ == '__main__':
    todos = fetchTodoList()
    if todos:
        layoutDoc = buildLayoutDocument(todos)
        ok = showOnSyncSign(layoutDoc)
        if ok:
            print('OK, Pushed %s todos to SyncSign' % len(todos))
        else:
            print('Oops, failed to push to SyncSign')
    else:
        print('Oops, failed to fetch todoist')
