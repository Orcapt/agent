"""
Local test script to verify the refactored Lambda handler.
"""
import json
import asyncio
from lambda_handler import handler

# Mock HTTP event (API Gateway)
http_event = {
    "httpMethod": "POST",
    "path": "/api/v1/send_message",
    "headers": {"Content-Type": "application/json"},
    "body": json.dumps({
        "message": "test message",
        "thread_id": "test_thread",
        "model": "gpt-4",
        "conversation_id": 1,
        "response_uuid": "test_resp",
        "message_uuid": "test_msg",
        "channel": "test_chan",
        "variables": [],
        "url": "http://localhost:8000/callback"
    })
}

# Mock SQS event
sqs_event = {
    "Records": [
        {
            "eventSource": "aws:sqs",
            "body": json.dumps({
                "message": "async message from SQS",
                "thread_id": "test_thread",
                "model": "gpt-4",
                "conversation_id": 1,
                "response_uuid": "test_resp",
                "message_uuid": "test_msg",
                "channel": "test_chan",
                "variables": [],
                "url": "http://localhost:8000/callback"
            })
        }
    ]
}

# Mock Cron event
cron_event = {
    "source": "aws.events",
    "detail-type": "Scheduled Event"
}

def test_lambda():
    print("--- Testing HTTP Event ---")
    res_http = handler(http_event, None)
    print(f"HTTP Response: {res_http}")

    print("\n--- Testing SQS Event ---")
    res_sqs = handler(sqs_event, None)
    print(f"SQS Response: {res_sqs}")

    print("\n--- Testing Cron Event ---")
    res_cron = handler(cron_event, None)
    print(f"Cron Response: {res_cron}")

if __name__ == "__main__":
    test_lambda()
