#!/usr/bin/env bash
set -euo pipefail

PORT="${TTS_PORT:-8001}"

exec uvicorn server:app --host 0.0.0.0 --port "${PORT}"
