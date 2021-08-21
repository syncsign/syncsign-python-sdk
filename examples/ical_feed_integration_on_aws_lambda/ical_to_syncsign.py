import traceback
import json
import copy
from datetime import datetime, date
import requests
from syncsign.client import Client
from syncsign.configuration import Configuration
from icalendar import Calendar, Event
import dateutil.tz as tz

# iCal Feed data source
ICALENDAR_FEED_URI = "https://p56-caldav.icloud.com/published/2/MTIyNDYwNTcyOTEyMjQ2MBhpY5IUmx8h8qfB6cUM6PVqka_NesTGKpw12MtDXRE0d-DszhU0TxUGwgVLKutElMhZ8MuJKtfSHWRwtaUJ73Y"
# See API Key in https://portal.sync-sign.com/#/setting
SYNCSIGN_TOKEN = '85d34cb6-7f12-4fc4-9813-154e34075615'
# The Display Node which you want to show the calendar events
SYNCSIGN_NODE_ID = '00124B001675CCAE'
# name of the Calendar, or a "room name"
TITLE_FOR_THIS_DISPLAY = "My Calendar"

DATETIME_FORMAT = '%H:%M'  # '%D %H:%M'
MAX_EVENTS_ON_DISPLAY = 5


def fetchData():
    # Request a list from data source: iCal feed
    # See https://icalendar.readthedocs.io/en/latest/
    try:
        ics = requests.get(
            ICALENDAR_FEED_URI,
            params={},
            headers={}).text
        cal = Calendar.from_ical(ics)

        events = []
        to_zone = tz.gettz('America/Chicago')
        now = datetime.now().astimezone(to_zone)
        dateNow = date.today()
        isBusy = False
        for event in cal.walk('vevent'):
            # check time range
            dtstart = event.get('dtstart').dt
            if type(dtstart) is datetime:
                epochStart = dtstart.timestamp()
                dtstart = dtstart.astimezone(to_zone)
            elif type(dtstart) is date:
                epochStart = datetime(
                    dtstart.year, dtstart.month, dtstart.day).timestamp()
            else:
                print('Date format not supported yet.')
                continue
            dtend = event.get('dtend').dt
            if type(dtend) is datetime:
                epochEnd = dtend.timestamp()
                dtend = dtend.astimezone(to_zone)
            elif type(dtend) is date:
                epochEnd = datetime(dtend.year, dtend.month,
                                    dtend.day).timestamp()
            else:
                print('Date format not supported yet.')
                continue

            if (type(dtend) is datetime and now > dtend) or \
               (type(dtend) is date and dateNow > dtend):
                print('Skip:', event.get('summary'), '@', epochStart)
                continue

            # parse event details
            description = event.get('description')
            summary = event.get('summary')
            location = event.get('location')
            events.append({
                # FIXME: if this event not occurs today, add a 'DATE' prefix
                'eStart': int(epochStart),
                'eEnd': int(epochEnd),
                'start': dtstart.strftime(DATETIME_FORMAT),
                'end': dtend.strftime(DATETIME_FORMAT),
                'description': description.to_ical().decode('utf-8') if description else 'No Description',
                'summary': summary.to_ical().decode('utf-8') if summary else '[ Untitled ]',
                'location': location.to_ical().decode('utf-8') if location else '-',
                # assume "all day event" if it's a "date" type
                'isAllDay': type(dtstart) is date
                # TODO: add creator, attendees,
            })
        print("Got %d events" % len(events))
        evts = events[:MAX_EVENTS_ON_DISPLAY]
        # sort events by start (epoch time)
        return isBusy, sorted(evts, key=lambda i: (i['eStart'],))
    except Exception as e:
        traceback.print_exc()
        print('Fetch calendar events failed:', e)


def buildLayoutDocument(isBusy, events):
    # Build a JSON based on the events data

    def _buildEventLine(evt):
        if evt.get('isAllDay'):
            return "All Day - "\
                + evt.get('summary')
        else:
            return evt.get('start') + " - " + evt.get('end') + " "\
                + evt.get('summary')

    tpl = {
        "background": {},
        "items": [
            {
                "type": "TEXT",
                "data": {
                    "font": "DDIN_48",
                    "block": {"x": 8, "y": 0, "w": 392, "h": 60},
                    "text": TITLE_FOR_THIS_DISPLAY
                }
            },
            {
                "type": "TEXT",
                "data": {
                    "font": "DDIN_24",
                    "textAlign": "RIGHT",
                    "block": {"x": 8, "y": 56, "w": 392, "h": 30},
                    "text": ""
                }
            }
        ]
    }
    EVENT_NOW_TPL = {
        "type": "TEXT",
                "data": {
                    "font": "DDIN_CONDENSED_32",
                    "block": {"x": 0, "y": 110, "w": 400, "h": 36},
                    "text": "{{TO_BE_REPLACED}}",
                    "textColor": "WHITE",
                    "backgroundColor": "BLACK",
                    "offset": {"x": 8, "y": 0}
                }
    }
    EVENT_UPCOMING_TPL = {
        "type": "TEXT",
                "data": {
                    "font": "DDIN_CONDENSED_32",
                    "block": {"x": 0, "y": 110, "w": 400, "h": 36},
                    "text": "{{TO_BE_REPLACED}}",
                    "offset": {"x": 8, "y": 0}
                }
    }

    tpl['items'][1]['data']['text'] = datetime.now().strftime(
        "%m/%d/%Y")  # or "%m/%d/%Y %H:%M"

    posY = 90
    evtIndex = 0
    if isBusy:
        # assume the first event is "ongoing now"
        x = copy.deepcopy(EVENT_NOW_TPL)
        x['data']['block']['y'] = posY
        x['data']['text'] = _buildEventLine(events[0])
        tpl['items'].append(x)
        evtIndex = 1
    else:  # Show "available until"...
        x = copy.deepcopy(EVENT_NOW_TPL)
        x['data']['block']['y'] = posY
        x['data']["textAlign"] = "CENTER"
        x['data']['text'] = "Available Until: " + events[0].get('start')
        tpl['items'].append(x)

    posY += 36
    for item in events[evtIndex:]:
        x = copy.deepcopy(EVENT_UPCOMING_TPL)
        x['data']['block']['y'] = posY
        x['data']['text'] = _buildEventLine(item)
        tpl['items'].append(x)
        posY += 36
    # print(json.dumps(tpl, indent=4))
    return tpl


def anyEventChanged(isBusy, events):
    # Compare state and events with previous saved
    #   Since we run this function every N minutes, most of the time
    #   we get the same events and no need to refresh the eink screen (to save energy)

    def loadPreviousState():
        try:
            with open('/tmp/.cached_events', 'r') as f:
                data = json.loads(f.read())
            return data.get('state'), data.get('events')
        except:
            print('Unable to load state')
        return None, None

    def saveCurrentState(isBusy, events):
        try:
            with open('/tmp/.cached_events', 'w') as f:
                f.write(json.dumps({"state": isBusy, "events": events}))
            print('state saved')
        except:
            print('Unable to save state')

    oldState, oldEvents = loadPreviousState()

    # Compare state
    if oldState != isBusy:
        saveCurrentState(isBusy, events)
        return True

    # Compare events
    # FIXME: compare visible elements only
    jsonNew = json.dumps(events, sort_keys=True)
    jsonOld = json.dumps(oldEvents, sort_keys=True)
    evtChanged = jsonNew != jsonOld
    if evtChanged:
        saveCurrentState(isBusy, events)
    return evtChanged


def showOnSyncSign(layoutDocument):
    # Add the layout document to the node's refresh queue
    print('Rendering on display node: %s' % SYNCSIGN_NODE_ID)
    renderId = None
    client = Client(api_key=SYNCSIGN_TOKEN)
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
    isBusy, events = fetchData()
    # print(isBusy, json.dumps(events, indent=4))
    if events:
        if anyEventChanged(isBusy, events):
            layoutDoc = buildLayoutDocument(isBusy, events)
            ok = showOnSyncSign(layoutDoc)
            if ok:
                print('OK, Pushed %s events to SyncSign' % len(events))
            else:
                print('Oops, failed to push to SyncSign')
        else:
            print('Events of the calendar are not changed, don\'t refresh the screen')
    else:
        print('Oops, failed to fetch events')
