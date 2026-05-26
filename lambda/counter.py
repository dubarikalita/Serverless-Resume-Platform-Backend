import json
import os
from decimal import Decimal

import boto3

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ.get(
    "TABLE_NAME",
    "serverless-resume-platform-counter",
)


def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    response = table.update_item(
        Key={"id": "visitor_count"},
        UpdateExpression="ADD #count :increment",
        ExpressionAttributeNames={"#count": "count"},
        ExpressionAttributeValues={":increment": Decimal("1")},
        ReturnValues="UPDATED_NEW",
    )

    count = int(response["Attributes"]["count"])

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Content-Type": "application/json",
        },
        "body": json.dumps({"count": count}),
    }
