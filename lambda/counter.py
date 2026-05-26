import json
import os
from decimal import Decimal

import boto3

TABLE_NAME = os.environ.get(
    "TABLE_NAME",
    "serverless-resume-platform-counter",
)


def lambda_handler(event, context):
    # boto3 initialised inside the handler so pytest can import
    # this file without needing real AWS credentials or a region.
    # In Lambda, the region is always available in the environment.
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=os.environ.get("AWS_DEFAULT_REGION", "ap-south-1"),
    )

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