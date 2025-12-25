"""
Lambda Handler - Entry Point
Supports direct HTTP, optional SQS offload, and cron-style events.
"""
import asyncio
import json
import os
import logging
from typing import Any, Dict

from fastapi import FastAPI
from mangum import Mangum
from orca import ChatMessage

from main import process_message, orca  # Reuse the same Orca handler and logic

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ensure event loop exists for Lambda (Python 3.11 quirk)
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


app = FastAPI(title="Orca SEO Agent Lambda")


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/v1/send_message")
async def send_message(data: ChatMessage):
    """
    Custom endpoint that either awaits the agent or offloads to SQS (if configured).
    """
    logger.info("Received message for lambda send_message")

    queue_url = os.environ.get("SQS_QUEUE_URL")
    if queue_url:
        import boto3

        boto3.client("sqs").send_message(
            QueueUrl=queue_url,
            MessageBody=data.model_dump_json(),
        )
        logger.info("Message queued to SQS")
        return {"status": "queued", "response_uuid": data.response_uuid}

    await process_message(data)
    return {"status": "ok", "response_uuid": data.response_uuid}


mangum_handler = Mangum(app, lifespan="off")


def handler(event: Dict[str, Any], context: Any):
    """
    Entry point for Lambda. Handles SQS/cron, otherwise forwards to FastAPI via Mangum.
    """
    logger.info("Lambda handler invoked with keys: %s", list(event.keys()))

    # Ensure an event loop is available (Python 3.11 Lambda threads)
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    # SQS event
    if "Records" in event and len(event["Records"]) > 0:
        first = event["Records"][0]
        if first.get("eventSource") == "aws:sqs":
            logger.info("Handling SQS batch: %d records", len(event["Records"]))
            for record in event["Records"]:
                try:
                    body = json.loads(record["body"])
                    data = ChatMessage(**body)
                    asyncio.run(process_message(data))
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Error processing SQS record: %s", exc)
            return {"statusCode": 200}

    # Cron / scheduled event
    if event.get("source") == "aws.events":
        logger.info("Handling cron/scheduled event")
        return {"statusCode": 200}

    # API Gateway / Function URL
    return mangum_handler(event, context)

