"""FastAPI server that wraps Piper TTS models for offline synthesis."""
from __future__ import annotations

import io
import logging
import os
import wave
from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

from piper import PiperVoice

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Local TTS Server", version="1.0.0")

voice_model: Optional[PiperVoice] = None


class SynthesisRequest(BaseModel):
    """Payload containing the text to be synthesized."""

    text: str
    speaker_id: Optional[int] = None


@app.on_event("startup")
def load_voice() -> None:
    """Loads the Piper voice when the service starts."""

    global voice_model

    model_path = os.environ.get("VOICE_MODEL", "/models/voice.onnx")
    config_path = os.environ.get("VOICE_CONFIG", "/models/voice.onnx.json")

    if not os.path.exists(model_path):
        msg = (
            f"Voice model not found at '{model_path}'. Mount the directory with your Piper "
            "voice files into the container."
        )
        logger.error(msg)
        raise RuntimeError(msg)

    if not os.path.exists(config_path):
        msg = (
            f"Voice config not found at '{config_path}'. The Piper JSON config must accompany "
            "the ONNX file."
        )
        logger.error(msg)
        raise RuntimeError(msg)

    logger.info("Loading Piper voice from %s", model_path)
    voice_model = PiperVoice.load(model_path=model_path, config_path=config_path)
    logger.info("Voice loaded successfully with sample rate %s", voice_model.sample_rate)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Simple endpoint to verify service readiness."""

    if voice_model is None:
        raise HTTPException(status_code=503, detail="Voice not loaded")
    return {"status": "ok"}


@app.post("/synthesize")
def synthesize(request: SynthesisRequest) -> Response:
    """Synthesizes the requested text and returns a WAV audio payload."""

    if voice_model is None:
        raise HTTPException(status_code=503, detail="Voice not loaded")

    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text must not be empty")

    try:
        audio_chunks = voice_model.synthesize_stream(text, speaker_id=request.speaker_id)
        audio_bytes = b"".join(audio_chunks)
    except Exception as exc:  # noqa: BLE001
        logger.exception("TTS synthesis failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(voice_model.sample_rate)
        wav_file.writeframes(audio_bytes)

    wav_bytes = buffer.getvalue()
    logger.info("Generated audio with %d bytes", len(wav_bytes))
    return Response(content=wav_bytes, media_type="audio/wav")


