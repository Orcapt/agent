# Lexia Agent Lambda Shipping Guide

This document is written for external agent developers who only have:

- **Lexia Starter Kit (Python v1)** or their own FastAPI/Flask project.
- The **`lexia` PyPI package**.
- Access to the hosted **`lexia-cli`** and platform APIs.

Nothing in this guide depends on any internal repositories. Follow the steps below to go from the starter kit to a production-grade Lambda deployment with Function URL + SQS trigger.

---

## 1. Prerequisites

| Tool / Access                              | Why it’s needed                               |
| ------------------------------------------ | --------------------------------------------- |
| Docker 24+ with BuildKit enabled           | Build the Lambda container image              |
| AWS account + IAM user/role                | Push to ECR and create Lambda/SQS resources   |
| AWS CLI v2 (`aws --version`)               | Login to ECR, test SQS, inspect Lambda        |
| `lexia-cli ≥ 1.12.0`                       | Runs `lexia ship` which talks to platform API |
| `lexia` PyPI package (`pip install lexia`) | Provides `ChatMessage`, `LexiaHandler`, etc.  |
| `jq` (optional)                            | Formatting JSON for curl/SQS tests            |
| Text editor + git                          | Modify starter kit and track your changes     |

> **AWS Permissions:** The IAM principal used by `lexia ship` must have `ecr:*`, `lambda:*`, `sqs:*`, `iam:PassRole`, and CloudWatch Logs access. Your platform admin can scope this via IAM policies.

---

## 2. Starter Kit Layout (Python v1)

```
lexia-starter-kit-python-v1/
├── app/
│   ├── main.py           # FastAPI entrypoint
│   ├── routers/          # Your HTTP routes
│   └── agents/           # Business logic calling lexia SDK
├── lambda_handler.py     # (add this file – see §4)
├── requirements.txt
├── requirements-lambda.txt
├── Dockerfile.lambda
└── .env.lambda (never commit)
```



Everything else in this guide happens inside this folder.

---

## 3. Implement or Import Your Agent Logic

1. Use the starter kit’s FastAPI routers (`app/routers/*.py`) to expose the endpoints you need. Example:

   ```python
   # app/routers/chat.py
   from fastapi import APIRouter
   from lexia import ChatMessage
   from app.agents.runner import run_agent

   router = APIRouter(prefix="/api/v1")

   @router.post("/chat")
   async def chat(msg: ChatMessage):
       return await run_agent(msg)
   ```

2. In `app/agents/runner.py`, import the `lexia` SDK plus any providers (OpenAI, Bedrock, custom tools).
3. Keep the code framework-agnostic; the Lambda wrapper will call the same functions you already run locally.

---

## 4. Add the Lambda Entry Point

Create `lambda_handler.py` in the project root. This example supports HTTP, SQS, and scheduled events using only the `lexia` package and Mangum:

```python
import os
import asyncio
from fastapi import FastAPI
from mangum import Mangum
from lexia import ChatMessage

from app.routers import chat  # import your routers
from app.agents.runner import run_agent

app = FastAPI(title="Lexia Agent")
app.include_router(chat.router)

# Ensure an event loop exists (Python 3.11 quirk on Lambda)
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/v1/send_message")
async def send_message(data: ChatMessage):
    queue_url = os.environ.get("SQS_QUEUE_URL")
    if queue_url:
        import boto3
        boto3.client("sqs").send_message(
            QueueUrl=queue_url,
            MessageBody=data.model_dump_json(),
        )
        return {"status": "queued", "response_uuid": data.response_uuid}
    await run_agent(data)
    return {"status": "ok", "response_uuid": data.response_uuid}

mangum_handler = Mangum(app, lifespan="off")

def handler(event, context):
    if "Records" in event and event["Records"][0].get("eventSource") == "aws:sqs":
        from app.agents.sqs import handle_sqs  # write this helper
        return handle_sqs(event)
    if event.get("source") == "aws.events":
        from app.agents.cron import handle_cron
        return handle_cron(event)
    return mangum_handler(event, context)
```

Notes:

- `handle_sqs` should parse `ChatMessage` objects and call `run_agent`. A reference implementation lives in `agent/gptclone-micro/src/sqs_handler.py` (you can copy logic if needed).
- Print environment variables at cold start to verify secrets arrived (mask actual secrets before logging).

---

## 5. Create a Lambda-Friendly Dockerfile

Save as `Dockerfile.lambda` at the project root:

```dockerfile
FROMpublic.ecr.aws/lambda/python:3.11

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements-lambda.txt .
RUN pip install --no-cache-dir -r requirements-lambda.txt

COPY app ./app
COPY lambda_handler.py .

CMD ["lambda_handler.handler"]
```

Tips:

- Keep `requirements-lambda.txt` minimal (FastAPI, lexia, mangum, boto3, and your providers).
- If you need system deps (e.g., `psycopg[binary]`), add `RUN yum install -y postgresql15 && yum clean all`.
- For extra assets (prompts, tools), add `COPY prompts ./prompts`.

---

## 6. Build & Push the Image to ECR

```bash
export ACCOUNT_ID=<your-account>
export REGION=us-east-1
export REPO=lexia-agent
export IMAGE="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:lambda-latest"

aws ecr get-login-password --region $REGION \
  | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

docker build -f Dockerfile.lambda -t lexia-agent-lambda:latest .
docker tag lexia-agent-lambda:latest "$IMAGE"
docker push "$IMAGE"
```

> If you do not have an ECR repo yet: `aws ecr create-repository --repository-name $REPO`.

---

## 7. Prepare Deployment Variables

Create `.env.lambda` (never commit) with everything your agent needs:

```
OPENAI_API_KEY=sk-...
DB_URL=postgresql+psycopg://user:pass@host:5432/db
STREAM_URL=https://centrifugo.your-org.com
STREAM_TOKEN=ST_xxx
LOG_LEVEL=info
```

The Lexia CLI will also inject:

- `SQS_QUEUE_URL` (auto-created per function)
- Any flags you pass via repeated `--env KEY=value`

---

## 8. Deploy via `lexia ship`

```bash
lexia login --api-url   --token <personal-access-token>

lexia ship my-agent \
  --image "$IMAGE" \
  --memory 2048 \
  --timeout 300 \
  --env-file ./.env.lambda \
  --env STREAM_URL=https://centrifugo.your-org.com \
  --env STREAM_TOKEN=<token>
```

What happens automatically:

1. Platform pulls your ECR image and updates the Lambda function (create or update).
2. A dedicated SQS queue (`my-agent-queue`) is created; its URL is added to `SQS_QUEUE_URL`.
3. Lambda Function URL is created (public, CORS `*`) and permissioned.
4. The CLI prints the Function URL + SQS URL + final env map. Save them in your ticket/runbook.

You can re-run `lexia ship` any time to push a new image or change env vars without creating duplicates.

---

## 9. Validate the Deployment

1. **Health check**
   ```bash
   curl https://<function-url>/health
   ```
2. **Direct invoke**
   ```bash
   curl -XPOST https://<function-url>/api/v1/send_message \
     -H "content-type: application/json" \
     -d '{"message":"hello","response_uuid":"lambda-test","stream_url":"https://centrifugo","stream_token":"token"}'
   ```
3. **SQS trigger**
   ```bash
   aws sqs send-message \
     --queue-url "$SQS_QUEUE_URL" \
     --message-body "$(jq -c . tests/test_payload.json)"
   ```
4. **Logs**
   ```bash
   lexia lambda logs my-agent --tail
   ```

Expect to see `[HANDLER] -> API` for HTTP calls and `[HANDLER] -> SQS` when the queue fires.

---

## 10. Environment Variable Reference

| Variable                         | Required?    | Source                   | Purpose                        |
| -------------------------------- | ------------ | ------------------------ | ------------------------------ |
| `OPENAI_API_KEY` / provider keys | ✅           | `.env.lambda` or `--env` | Model access                   |
| `STREAM_URL`, `STREAM_TOKEN`     | ✅           | payload + fallback env   | Centrifugo/Websocket streaming |
| `DB_URL`, `REDIS_URL`, etc.      | ✅ (if used) | `.env.lambda`            | Backing services               |
| `SQS_QUEUE_URL`                  | Auto         | Set by platform          | Decides async vs direct mode   |
| `LOG_LEVEL`, feature flags       | Optional     | `.env.lambda`            | Tuning + observability         |

The handler prints every key (value masked) on cold start so you can confirm they are present.

---

## 11. Troubleshooting

| Symptom                             | Root cause                                        | Fix                                                                                                |
| ----------------------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `TLS handshake timeout` during push | Slow network / ECR region mismatch                | Re-run `lexia ship` (retries enabled) or push from an EC2 builder in the same region               |
| `Runtime.ExitError` right away      | Wrong base image or missing handler               | Use `public.ecr.aws/lambda/python:3.11` and `CMD ["lambda_handler.handler"]`                       |
| Function URL returns 403            | Permission missing                                | Re-run `lexia ship`; it re-applies `lambda:InvokeFunctionUrl` policy                               |
| Env vars missing                    | Incorrect `--env` syntax or missing `.env.lambda` | Use `KEY=value` pairs; CLI prints final map—double-check before confirming                         |
| Centrifugo points to internal URL   | `stream_url` in payload was `null`                | Ensure the invoking service sends `stream_url`/`stream_token`; fallback env can be set             |
| SQS never triggers                  | Event source mapping disabled                     | `lexia ship` recreates it; or run `aws lambda list-event-source-mappings --function-name my-agent` |

Need more help? Collect the latest CloudWatch log stream and open a ticket with the Function name + timestamp.

---

## 12. Deployment Checklist

- [ ] Clone/update `lexia-starter-kit-python-v1`
- [ ] `lambda_handler.py` in place with HTTP + SQS logic
- [ ] `requirements-lambda.txt` trimmed and tested locally
- [ ] `Dockerfile.lambda` builds successfully
- [ ] Image pushed to ECR (`IMAGE` recorded)
- [ ] `.env.lambda` stored securely and passed to `lexia ship`
- [ ] `lexia ship <function>` executed without errors
- [ ] Function URL health check passes
- [ ] SQS message processed (`[SQS] Processing …` in logs)

Once all boxes are checked, your starter-kit agent is running on AWS Lambda with the same streaming behavior as your local dev environment—no internal repositories required.

---

## 13. Reference Implementation (Starter Kit Files)

Use these files as-is or adapt them inside your starter kit project.

### `lambda_handler.py`

```python
"""
Lambda Handler - Entry Point
Contains the custom endpoint that awaits responses.
"""
import os
import asyncio
from fastapi import FastAPI
from mangum import Mangum
from lexia import ChatMessage

from src.chatbot_handler import process_message, lexia
from src.sqs_handler import handle_sqs, handle_cron

# Fix for Python 3.11+ event loop issue
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

print("[LAMBDA] Loading...", flush=True)

app = FastAPI(title="GPTClone Lambda")


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/v1/send_message")
async def send_message(data: ChatMessage):
    """
    Custom endpoint that awaits responses or offloads to SQS.
    """
    print(f"[API] Received: {data.message[:50]}...", flush=True)

    queue_url = os.environ.get('SQS_QUEUE_URL')

    if queue_url:
        # SQS mode
        import boto3
        sqs = boto3.client('sqs')
        sqs.send_message(QueueUrl=queue_url, MessageBody=data.model_dump_json())
        print("[API] → SQS", flush=True)
        return {"status": "queued", "response_uuid": data.response_uuid}

    # Direct mode - AWAIT!
    print("[API] → Direct (await)", flush=True)
    await process_message(data)
    print("[API] Done!", flush=True)
    return {"status": "ok", "response_uuid": data.response_uuid}


# Mangum
mangum_handler = Mangum(app, lifespan="off")


def handler(event, context):
    print("=" * 50, flush=True)
    print(f"[HANDLER] Event keys: {list(event.keys())}", flush=True)
    print("=" * 50, flush=True)

    # SQS
    if 'Records' in event and len(event['Records']) > 0:
        if event['Records'][0].get('eventSource') == 'aws:sqs':
            print("[HANDLER] → SQS", flush=True)
            return handle_sqs(event)

    # Cron
    if event.get('source') == 'aws.events':
        print("[HANDLER] → Cron", flush=True)
        return handle_cron(event)

    # API
    print("[HANDLER] → API", flush=True)
    return mangum_handler(event, context)


print("[LAMBDA] Ready!", flush=True)
```

### `src/sqs_handler.py`

```python
"""
SQS Handler - process incoming SQS records.
"""
import json
import asyncio
from lexia import ChatMessage
from src.chatbot_handler import process_message, lexia


def update_centrifugo(data: ChatMessage):
    """Update Centrifugo URL/token from ChatMessage payload."""
    stream_url = getattr(data, 'stream_url', None)
    stream_token = getattr(data, 'stream_token', None)

    if stream_url and hasattr(lexia, 'stream_client') and lexia.stream_client:
        lexia.stream_client.url = stream_url
        if stream_token:
            lexia.stream_client.api_key = stream_token
        print(f"[SQS] Centrifugo updated: {stream_url}", flush=True)


def handle_sqs(event):
    """Process each SQS record and kick off the agent."""
    records = event.get('Records', [])
    print(f"[SQS] Processing {len(records)} messages", flush=True)

    for record in records:
        try:
            body = json.loads(record['body'])
            data = ChatMessage(**body)

            # Refresh Centrifugo connection before streaming
            update_centrifugo(data)

            # Process the message synchronously
            asyncio.run(process_message(data))
            print(f"[SQS] Done: {data.response_uuid}", flush=True)

        except Exception as e:
            print(f"[SQS] Error: {e}", flush=True)

    return {"statusCode": 200}


def handle_cron(event):
    """Entry point for scheduled/cron events."""
    print("[CRON] Running scheduled task...", flush=True)
    # Place recurring maintenance logic here
    return {"statusCode": 200}
```

### `src/chatbot_handler.py`

```python
"""
Chatbot Handler - lightweight Lambda demo.
Streams a static message to verify the pipeline.
"""
import asyncio
from lexia import ChatMessage, LexiaHandler

lexia = LexiaHandler()

# Demo payload
TEST_MESSAGE = """Hello! This is a streaming test coming from AWS Lambda.
If you can read this, everything is working correctly.
Streaming succeeded! 🎉"""


async def process_message(data: ChatMessage):
    """
    Streaming demo that emits a static message chunk-by-chunk.
    """
    print(f"[PROCESS] Starting: {data.response_uuid}", flush=True)

    # Update Centrifugo endpoint when provided
    stream_url = getattr(data, 'stream_url', None)
    stream_token = getattr(data, 'stream_token', None)

    if stream_url and hasattr(lexia, 'stream_client') and lexia.stream_client:
        print(f"[PROCESS] Centrifugo: {stream_url}", flush=True)
        lexia.stream_client.url = stream_url
        if stream_token:
            lexia.stream_client.api_key = stream_token

    # Stream the demo text word-by-word
    full_msg = ''
    words = TEST_MESSAGE.split(' ')
    total = len(words)

    print(f"[STREAM] Sending {total} words...", flush=True)

    for i, word in enumerate(words):
        chunk = word + ' '
        full_msg += chunk

        try:
            lexia.stream_chunk(data, chunk)
            print(f"[STREAM] [{i+1}/{total}] OK", flush=True)
        except Exception as e:
            print(f"[STREAM] [{i+1}/{total}] Error: {e}", flush=True)
            break

        await asyncio.sleep(0.05)

    # Finalize the response stream
    try:
        lexia.complete_response(data, full_msg, None)
        print("[PROCESS] Complete!", flush=True)
    except Exception as e:
        print(f"[PROCESS] Complete error: {e}", flush=True)
```

Happy shipping! 🚀