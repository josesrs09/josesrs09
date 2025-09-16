"""Offline speech agent orchestrator that links STT, LLM and TTS services."""
from __future__ import annotations

import argparse
import io
import logging
import sys
import threading
from collections import deque
from pathlib import Path
from typing import Deque, Dict, Iterable, Iterator, List

import numpy as np
import requests
import sounddevice as sd
import wave
import webrtcvad
import yaml
from faster_whisper import WhisperModel
from contextlib import contextmanager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")


class ConfigError(RuntimeError):
    """Raised when configuration values are missing or invalid."""


class VADSegmenter:
    """Streams audio from the microphone and yields voice segments using WebRTC VAD."""

    def __init__(
        self,
        sample_rate: int,
        frame_duration_ms: int,
        padding_duration_ms: int,
        vad_aggressiveness: int,
    ) -> None:
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.padding_duration_ms = padding_duration_ms
        self.frame_length = int(sample_rate * frame_duration_ms / 1000)
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        self.channels = 1
        self._stop_event = threading.Event()

    def stop(self) -> None:
        """Signals the stream to stop."""

        self._stop_event.set()

    def segments(self) -> Iterator[bytes]:
        """Generator that yields individual speech segments as PCM16 bytes."""

        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.frame_length,
            dtype="int16",
            channels=self.channels,
        ) as stream:
            logger.info("Escuchando el micrófono… (Ctrl+C para salir)")
            frames = self._frame_generator(stream)
            for segment in self._vad_collector(frames):
                if self._stop_event.is_set():
                    break
                yield segment

    def _frame_generator(self, stream: sd.RawInputStream) -> Iterator[bytes]:
        """Reads audio frames from the input stream."""

        while not self._stop_event.is_set():
            data, overflowed = stream.read(self.frame_length)
            if overflowed:
                logger.warning("Desbordamiento de audio detectado")
            if not data:
                continue
            yield bytes(data)

    def _vad_collector(self, frames: Iterable[bytes]) -> Iterator[bytes]:
        """Groups frames into voiced segments using a ring buffer."""

        num_padding_frames = int(self.padding_duration_ms / self.frame_duration_ms)
        ring_buffer: Deque[tuple[bytes, bool]] = deque(maxlen=num_padding_frames)
        triggered = False
        voiced_frames: List[bytes] = []

        for frame in frames:
            if len(frame) == 0:
                continue

            is_speech = False
            try:
                is_speech = self.vad.is_speech(frame, self.sample_rate)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Error evaluando VAD: %s", exc)
                continue

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > 0.9 * ring_buffer.maxlen:
                    triggered = True
                    voiced_frames.extend(f for f, _ in ring_buffer)
                    ring_buffer.clear()
                    logger.debug("Voz detectada")
            else:
                voiced_frames.append(frame)
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > 0.9 * ring_buffer.maxlen:
                    logger.debug("Fin de segmento de voz")
                    yield b"".join(voiced_frames)
                    ring_buffer.clear()
                    voiced_frames = []
                    triggered = False

        if voiced_frames:
            yield b"".join(voiced_frames)


class VoiceAgent:
    """Coordinates VAD, STT, LLM and TTS services to build a voice agent."""

    def __init__(self, config_path: Path) -> None:
        self.config = self._load_config(config_path)
        audio_cfg = self.config["audio"]
        self.segmenter = VADSegmenter(
            sample_rate=audio_cfg["sample_rate"],
            frame_duration_ms=audio_cfg["frame_duration_ms"],
            padding_duration_ms=audio_cfg["padding_duration_ms"],
            vad_aggressiveness=audio_cfg.get("vad_aggressiveness", 2),
        )

        stt_cfg = self.config["stt"]
        model_path = stt_cfg.get("model_path")
        if not model_path:
            raise ConfigError("'stt.model_path' es obligatorio")

        compute_type = stt_cfg.get("compute_type", "int8")
        logger.info("Cargando modelo STT desde %s", model_path)
        self.stt_model = WhisperModel(model_path, compute_type=compute_type)
        self.stt_language = stt_cfg.get("language")
        self.stt_beam_size = stt_cfg.get("beam_size", 5)

        self.llm_cfg = self.config["llm"]
        self.tts_cfg = self.config["tts"]
        playback_cfg = self.config.get("playback", {})
        self.wait_playback = playback_cfg.get("wait_for_completion", True)

        self.history: List[Dict[str, str]] = []
        system_prompt = self.llm_cfg.get("system_prompt")
        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})

    @staticmethod
    def _load_config(path: Path) -> Dict[str, Dict[str, object]]:
        if not path.exists():
            raise ConfigError(f"Archivo de configuración no encontrado: {path}")
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        required_sections = {"audio", "stt", "llm", "tts"}
        missing = required_sections.difference(data.keys())
        if missing:
            raise ConfigError(f"Faltan secciones en la configuración: {', '.join(sorted(missing))}")
        return data

    def run(self) -> None:
        """Starts the agent loop."""

        try:
            for segment in self.segmenter.segments():
                try:
                    transcription = self._transcribe(segment)
                    if not transcription:
                        continue
                    logger.info("Usuario: %s", transcription)
                    reply = self._query_llm(transcription)
                    logger.info("Asistente: %s", reply)
                    audio_bytes = self._synthesize(reply)
                    self._play_audio(audio_bytes)
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Error procesando el segmento: %s", exc)
        except KeyboardInterrupt:
            logger.info("Interrupción manual, cerrando el agente…")
        finally:
            self.segmenter.stop()

    def _transcribe(self, audio_bytes: bytes) -> str:
        if not audio_bytes:
            return ""

        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
        if audio_np.size == 0:
            return ""
        audio_np /= 32768.0

        segments, _info = self.stt_model.transcribe(
            audio_np,
            language=self.stt_language,
            beam_size=self.stt_beam_size,
        )
        text = " ".join(segment.text.strip() for segment in segments).strip()
        return text

    def _query_llm(self, user_text: str) -> str:
        messages = self.history + [{"role": "user", "content": user_text}]
        payload = {
            "messages": messages,
            "temperature": self.llm_cfg.get("temperature", 0.7),
            "max_tokens": self.llm_cfg.get("max_tokens", 512),
        }
        url = self.llm_cfg["url"]
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.exception("Error al contactar el LLM: %s", exc)
            raise

        data = response.json()
        reply = data.get("text")
        if not reply:
            raise RuntimeError(f"Respuesta inválida del LLM: {data}")

        self.history.extend(
            [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": reply},
            ]
        )
        return reply.strip()

    def _synthesize(self, text: str) -> bytes:
        url = self.tts_cfg["url"]
        payload = {"text": text}
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.exception("Error al contactar el TTS: %s", exc)
            raise
        return response.content

    def _play_audio(self, wav_bytes: bytes) -> None:
        if not wav_bytes:
            return
        with wave_open(wav_bytes) as (audio, sample_rate):
            sd.play(audio, samplerate=sample_rate)
            if self.wait_playback:
                sd.wait()


@contextmanager
def wave_open(wav_bytes: bytes) -> Iterator[tuple[np.ndarray, int]]:
    """Utility context manager that yields PCM data and sample rate from WAV bytes."""

    with io.BytesIO(wav_bytes) as buffer:
        with wave.open(buffer, "rb") as wav_reader:
            frames = wav_reader.readframes(wav_reader.getnframes())
            sample_rate = wav_reader.getframerate()
            audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
            audio /= 32768.0
            yield audio, sample_rate


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Agente de voz offline")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/agent.yaml"),
        help="Ruta al archivo de configuración YAML",
    )
    return parser.parse_args(args)


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    agent = VoiceAgent(args.config)
    agent.run()


if __name__ == "__main__":
    main()
