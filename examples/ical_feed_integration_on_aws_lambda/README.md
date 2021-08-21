
## Example: iCal & SyncSign integration

This is a simple example shows how to:
- Read data from a third party system (an iCal feed URL here)
- Extract the information you are going to show on [SyncSign e-Ink Displays](https://sync-sign.com/display/)
- Fill the information into the [template](https://dev.sync-sign.com/hubsdk/guides/render_layout.html), and push it to SyncSign Cloud Server
- Then the display node is queued to refresh the screen with the latest data

## How to run this example on local development machine?

- Go to where the ical_to_syncsign.py locates:
- Run:

```
pip3 install -r requirements.txt
python3 ical_to_syncsign.py
```

- Output example:
```
Skip: Great Work! @ 1629539100.0
Skip: Interview Joe @ 1629457200.0
Got 6 events
state saved
Rendering on display node: 00124B001675CCAE
Render ID: 39421a08-9e9d-442b-b592-5b2ea433a5de
OK, Pushed 5 events to SyncSign
```

- Then it will take abount 30s to 1min to refresh the calendar events on the e-paper display

## How to deploy this example on AWS Lambda?

### Step 1. Create the code package

- Before proceed, your development machine should have Python 3.x and pip installed.
- Modify the ICALENDAR_FEED_URI/SYNCSIGN_TOKEN/SYNCSIGN_NODE_ID in ical_to_syncsign.py accordingly.
- Run this command on a path where the lambda_function.py and ical_to_syncsign.py locates:

```
pip3 install --target . -r requirements.txt
zip -r ../upload.zip .
```

- Then you got a "upload.zip" on upper folder

### Step 2. Upload the code package to AWS Lambda

- Sign in or Create an account on the Amazon AWS: `https://aws.amazon.com`
- Go to AWS Lambda dashboard, click [Create function]
- Select "Author from scratch"; Input a "Function name" (e.g. iCalToSyncSign); Select "Python 3.8" as "Runtime". Hit [Create function]
- On the "Code source" block, select the [Upload from] > [.zip File]; Select the "upload.zip" we just created
- After successfully uploading, click the [Test] on "Code source" block, input any "Event Name", and hit the [Create]
- Click the [Test] again to run the test, you will see this response:

```
{
  "statusCode": 204,
  "body": "OK, Pushed 5 events to SyncSign"
}
```

### Step 3. Create a schedule to call the AWS Lambda function

- We can run the lambda at an interval, e.g. every 5 minutes.
- Expand the "Function overview" block; Click [Add trigger]
- Select "EventBridge (CloudWatch Events)", then "Create a new rule", name it as "poll_iCal_5min"
- In "Schedule expression", input `cron(1/5 9-18 ? * MON-FRI *)`, to run the lambda once per 5 minutes on work days 9AM to 6PM
- Click [Add]
- Please note the schedule hour is on the GMT timezone. Learn more about CRON expression: https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html

### Note

- We run this example on lambda every 5 minutes, however during most of the time, the events are unchanged and we dont want to refresh the eink screen.
- So we need to compare the current state and events to previously pushed. This example uses `/tmp` as persistent storage to cache state and events.
- However if the function runs on AWS lambda, the /tmp area is preserved for the lifetime of the execution environment and provides a transient cache for data between invocations.
- Each time a new execution environment is created, this area is deleted. To keep the environment for the /tmp storage), we must invoke the lambda at a short interval (e.g. 5 minutes).
- If you see "Unable to load state" in the "CloudWatch Logs Insights", this log means `/tmp` was deleted before current invocation.
- [Reference](https://aws.amazon.com/cn/blogs/compute/choosing-between-aws-lambda-data-storage-options-in-web-apps/)
