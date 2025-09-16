"""FastAPI server exposing a local llama.cpp model via a chat completion API."""
from __future__ import annotations

import logging
import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from llama_cpp import Llama

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Local LLM Server", version="1.0.0")


class Message(BaseModel):
    """Represents a chat message following the OpenAI schema."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """Request payload for chat completions."""

    messages: List[Message]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.95


class ChatResponse(BaseModel):
    """Response payload returned to clients."""

    text: str


llm_model: Optional[Llama] = None


@app.on_event("startup")
def load_model() -> None:
    """Loads the llama.cpp model when the server starts."""

    global llm_model
    model_path = os.environ.get("MODEL_PATH", "/models/model.gguf")
    context_size = int(os.environ.get("CONTEXT_SIZE", "4096"))
    n_threads = int(os.environ.get("N_THREADS", "4"))
    gpu_layers = int(os.environ.get("GPU_LAYERS", "0"))

    if not os.path.exists(model_path):
        msg = (
            f"Model file not found at '{model_path}'. Make sure to mount the directory "
            "containing your GGUF model into the container."
        )
        logger.error(msg)
        raise RuntimeError(msg)

    logger.info("Loading model from %s", model_path)
    llm_model = Llama(
        model_path=model_path,
        n_ctx=context_size,
        n_threads=n_threads,
        n_gpu_layers=gpu_layers,
        chat_format="chatml",
    )
    logger.info("Model loaded successfully")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Simple healthcheck endpoint."""

    if llm_model is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    return {"status": "ok"}


@app.post("/v1/chat/completions", response_model=ChatResponse)
def chat_completion(request: ChatRequest) -> ChatResponse:
    """Generates a chat response using the local llama.cpp backend."""

    if llm_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if not request.messages:
        raise HTTPException(status_code=400, detail="At least one message is required")

    try:
        completion = llm_model.create_chat_completion(
            messages=[{"role": msg.role, "content": msg.content} for msg in request.messages],
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("LLM inference failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    try:
        text = completion["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        logger.exception("Unexpected response schema: %s", completion)
        raise HTTPException(status_code=500, detail="Malformed model response") from exc

    logger.info("Response generated: %s", text)
    return ChatResponse(text=text)


