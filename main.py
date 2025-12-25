import asyncio
import logging
import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from orca import (
    ChatMessage,
    OrcaHandler,
    add_standard_endpoints,
    create_orca_app,
    setup_logging,
    get_logger,
    get_variable_value,
)
from openai import AsyncOpenAI

from seo_agent import SEO_SYSTEM_PROMPT

load_dotenv()

# Setup logging
# In Lambda, /var/task is read-only, so use /tmp for log files
is_lambda = os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None
setup_logging(
    level=logging.INFO,
    log_file="/tmp/main.log" if is_lambda else "main.log",
    enable_colors=not is_lambda  # Disable colors in Lambda (CloudWatch doesn't support them)
)
logger = get_logger(__name__)

# Determine dev mode from environment (default: False for production)
dev_mode = os.getenv("ORCA_DEV_MODE", "false").lower() == "true"

# Initialize Orca handler
orca = OrcaHandler(dev_mode=dev_mode)

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


async def _stream_completion(messages: List[Dict[str, Any]], model: str, data: ChatMessage):
    """Stream completion chunks back to Orca clients."""
    full_response = ""
    
    # Get OpenAI API key from environment or variables
    api_key = get_variable_value(data.variables, "OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment or variables")
    
    openai_client = AsyncOpenAI(api_key=api_key)
    stream = await openai_client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        temperature=0.7,
    )

    # Create session for streaming
    session = orca.begin(data)
    
    try:
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if not delta:
                continue

            full_response += delta
            # Stream chunk using session
            await asyncio.to_thread(session.stream, delta)

        # Complete response
        await asyncio.to_thread(session.close)
    except Exception as e:
        logger.exception("Error during streaming")
        await asyncio.to_thread(session.error, "An error occurred during streaming", exception=e)
        await asyncio.to_thread(session.close)
        raise


async def process_message(data: ChatMessage):
    """
    Entry point for Orca standard endpoint.
    Streams the SEO expert response back to clients.
    """
    try:
        # Build chat history for the SEO persona
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SEO_SYSTEM_PROMPT},
            {"role": "user", "content": data.message or ""},
        ]

        model = data.model or DEFAULT_MODEL
        await _stream_completion(messages, model, data)

    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to process message")
        session = orca.begin(data)
        try:
            error_text = "An error occurred while generating the response."
            await asyncio.to_thread(session.error, error_text, exception=exc)
        finally:
            await asyncio.to_thread(session.close)


# FastAPI app exposed to Orca / clients
app = create_orca_app(
    title="Orca SEO Agent",
    version="1.0.0",
    description="SEO Expert agent with streaming responses built on Orca SDK.",
)

add_standard_endpoints(
    app,
    conversation_manager=None,
    orca_handler=orca,
    process_message_func=process_message,
)

@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", os.getenv("AGENT_PORT", "5001")))
    docs_base = f"http://localhost:{port}"

    print("🚀 Starting Orca SEO Agent...")
    print("=" * 60)
    
    # Display mode
    if dev_mode:
        print("🔧 DEV MODE ACTIVE - No Centrifugo required!")
        print("   Use ORCA_DEV_MODE=false for production")
    else:
        print("🟢 PRODUCTION MODE - Centrifugo/WebSocket streaming")
        print("   Use ORCA_DEV_MODE=true for local development")
    
    print("=" * 60)
    print(f"📖 API Documentation: {docs_base}/docs")
    print(f"🔍 Health Check: {docs_base}/api/v1/health")
    print(f"💬 Chat Endpoint: {docs_base}/api/v1/send_message")
    
    if dev_mode:
        print(f"📡 SSE Stream: {docs_base}/api/v1/stream/{{channel}}")
        print(f"📊 Poll Stream: {docs_base}/api/v1/poll/{{channel}}")
    
    print("=" * 60)
    print("\n✨ Features:")
    print("   - Clean integration with Orca SDK")
    print("   - SEO Expert agent with OpenAI")
    print("   - Streaming responses")
    print("   - Comprehensive error handling")
    
    if dev_mode:
        print("   - Dev mode streaming (SSE, no Centrifugo)")
    else:
        print("   - Production streaming (Centrifugo/WebSocket)")
    
    print("\n🔧 Customize the process_message() function to add your AI logic!")
    print("=" * 60)
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=port)
