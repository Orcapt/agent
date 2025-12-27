"""
Lambda Handler - Refactored with Orca Factory
Supports HTTP (with SQS offload), SQS (async task), and Cron events automatically.
"""
import logging
from orca import create_hybrid_handler
from main import process_message

# Create the universal Lambda handler using the Orca factory
# This handles:
# 1. FastAPI + Mangum for HTTP events
# 2. Automatic SQS offloading if SQS_QUEUE_URL is set
# 3. Direct execution of process_message for SQS records
# 4. Detection of Cron/Scheduled events
handler = create_hybrid_handler(
    process_message_func=process_message,
    app_title="Orca SEO Agent Lambda",
    level=logging.INFO
)
