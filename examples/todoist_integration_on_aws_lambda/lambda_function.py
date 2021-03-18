import todoist

def lambda_handler(event, context):
    todos = todoist.fetchTodoList()
    if todos:
        layoutDoc = todoist.buildLayoutDocument(todos)
        ok = todoist.showOnSyncSign(layoutDoc)
        if ok:
            result = 'OK, Pushed %s todos to SyncSign' % len(todos)
        else:
            result = 'Oops, failed to push to SyncSign'
    else:
        result = 'Oops, failed to fetch todoist'

    return {
        'statusCode': 200,
        'body': result
    }
