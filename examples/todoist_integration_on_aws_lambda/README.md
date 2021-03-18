
## How to Deploy this example on AWS Lambda?

### Step 1. Create the code package

- Before proceed, your development machine should have Python 3.x and pip installed.
- Modify the TODOIST_TOKEN/SYNCSIGN_TOKEN/SYNCSIGN_NODE_ID in todoist.py accordingly.
- Run this command on a path where the lambda_function.py and todoist.py locates:

```
pip install --target . syncsign
zip -r ../upload.zip .
```
- Then you got a "upload.zip" on upper folder

### Step 2. Upload code package to AWS Lambda

- Sign in or Create an account on the Amazon AWS: https://aws.amazon.com
- Go to AWS Lambda dashboard, click [Create function]
- Select "Author from scratch"; Input a "Function name"; Select "Python 3.8" as "Runtime". Hit [Create function]
- On the "Code source" block, select the [Upload from] > [.zip File]; Select the "upload.zip" we just created
- After successfully uploading, click the [Test] on "Code source" block, input any "Event Name", and hit the [Create]
- Click the [Test] again to run the test, you will see this response:

```
{
  "statusCode": 200,
  "body": "OK, Pushed 3 todos to SyncSign"
}
```

### Step 3. Create a schedule to call the AWS Lambda function

- We can run the lambda at an interval, e.g. twice per day.
- Expand the "Function overview" block; Click [Add trigger]
- Select "EventBridge (CloudWatch Events)", then "Create a new rule", name it as "twice_per_day"
- In "Schedule expression", input `cron(0 8,13 ? * MON-FRI *)`, to run the lambda at 8:00 and 13:00 on work days
- Click [Add]
- Please note the schedule hour is on the GMT timezone. Learn more about CRON expression: https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html
