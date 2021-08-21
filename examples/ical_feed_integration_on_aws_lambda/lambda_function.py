import ical_to_syncsign as itos

def lambda_handler(event, context):
    isBusy, events = itos.fetchData()
    if events:
        if itos.anyEventChanged(isBusy, events):
            layoutDoc = itos.buildLayoutDocument(isBusy, events)
            ok = itos.showOnSyncSign(layoutDoc)
            if ok:
                result = 'OK, Pushed %s events to SyncSign' % len(events)
                code = 204
            else:
                result = 'Oops, failed to push to SyncSign'
                code = 500
        else:
            result = 'Events of the calendar are not changed, don\'t refresh the screen'
            code = 204
    else:
        result = 'Oops, failed to fetch events'
        code = 503

    return {
        'statusCode': code,
        'body': result
    }
