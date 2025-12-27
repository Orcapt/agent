import os
import asyncio
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI

from orca import create_agent_app, ChatMessage, Variables
from seo_agent import SEO_SYSTEM_PROMPT

load_dotenv()

# The factory handles logging, dev_mode detection, and app creation automatically.
async def process_message(data: ChatMessage):
    """
    Main processing logic for the SEO Expert agent.
    """
    # orca is globally available if injected or we can use the injected handler.
    # In this case, we'll use the session API as recommended.
    session = orca.begin(data)
    
    try:
        # 1. Access variables safely
        vars = Variables(data.variables)
        api_key = vars.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            session.error("OPENAI_API_KEY not found")
            return

        # 2. Build messages
        messages = [
            {"role": "system", "content": SEO_SYSTEM_PROMPT},
            {"role": "user", "content": data.message or ""},
        ]

        # 3. Call OpenAI with streaming
        client = AsyncOpenAI(api_key=api_key)
        stream = await client.chat.completions.create(
            model=data.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            stream=True,
            temperature=0.7,
        )

        session.loading.start("thinking")
        
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                session.stream(delta)

        session.loading.end("thinking")
        
        # 4. Finalize
        session.close()

    except Exception as e:
        session.error("SEO analysis failed", exception=e)

# Create the app and handler using the factory
app, orca = create_agent_app(
    process_message_func=process_message,
    title="Orca SEO Agent",
    version="1.0.0",
    description="Professional SEO Expert Agent powered by Orca SDK."
)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
