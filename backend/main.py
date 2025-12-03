import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.models import ChatRequest, ChatResponse
from backend.rag import retrieve_context, generate_answer, close_clients

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await close_clients()

app = FastAPI(lifespan=lifespan)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def event_generator():
        try:
            # 1. Retrieve Context
            sources, context = await retrieve_context(request.query)

            # 2. Yield Sources
            yield ChatResponse(sources=sources).model_dump_json(exclude_unset=True) + "\n"

            # 3. Stream Answer
            stream = await generate_answer(request.query, context)
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield ChatResponse(token=content).model_dump_json(exclude_unset=True) + "\n"

        except Exception as e:
            logger.error(f"Error in chat_stream: {e}")
            yield ChatResponse(error=str(e)).model_dump_json(exclude_unset=True) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
