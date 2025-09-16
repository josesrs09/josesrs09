# Agente de voz 100 % local (STT → LLM → TTS)

Este repositorio contiene una pila completa para ejecutar un asistente de voz estilo ElevenLabs sin conexión a Internet y sin depender de servicios de pago. La solución se divide en tres componentes principales:

1. **Reconocimiento de voz (STT)**: basado en Whisper a través de `faster-whisper` y ejecutado de forma local desde el orquestador.
2. **Modelo de lenguaje (LLM)**: expuesto mediante una API compatible con chat completions que utiliza `llama.cpp` dentro de un contenedor Docker.
3. **Síntesis de voz (TTS)**: servicio FastAPI que envuelve modelos de `piper-tts` y produce audio WAV localmente.

Un orquestador en Python enlaza estos servicios, escucha el micrófono con detección de voz (VAD), transcribe el audio, genera la respuesta con el LLM y la reproduce en voz.

## Estructura del proyecto

```
├── configs/agent.yaml          # Parámetros del orquestador
├── docker-compose.yml          # Orquesta los servicios LLM y TTS
├── llm/                        # Dockerfile y servidor del modelo de lenguaje
├── tts/                        # Dockerfile y servidor TTS basado en Piper
├── orchestrator/               # Código del orquestador y requisitos locales
└── models/                     # Carpeta (ignoradas por git) para alojar los modelos
```

## Requisitos previos

- Docker y Docker Compose.
- Python 3.10+ para el orquestador.
- Dependencias del sistema para audio en Linux:
  ```bash
  sudo apt-get install -y portaudio19-dev libsndfile1
  ```
- Modelos descargados previamente (puede hacerse en otra máquina con Internet y copiarse offline):
  - **STT**: modelo CTranslate2 de Whisper. Por ejemplo, `faster-whisper-small` convertido a formato CTranslate2 y colocado en `models/stt/whisper-small`.
  - **LLM**: modelo GGUF compatible con `llama.cpp` (p.ej. `mistral-7b-instruct.Q4_K_M.gguf`) en `models/llm/model.gguf`.
  - **TTS**: voz de Piper (archivos `.onnx` y `.json`). Ejemplo: `es_ES-mls_8429-low.onnx` y su `.json` en `models/tts/`.

> **Nota:** Los modelos no se incluyen en el repositorio y deben descargarse por separado. La pila funciona completamente offline una vez que los archivos están disponibles localmente.

## Puesta en marcha

### 1. Preparar el entorno de modelos

Cree la estructura de carpetas esperada y copie los modelos previamente descargados:

```
models/
├── llm/
│   └── model.gguf
├── stt/
│   └── whisper-small/  # Contiene los ficheros del modelo CTranslate2
└── tts/
    ├── voice.onnx
    └── voice.onnx.json
```

Ajuste los nombres en `configs/agent.yaml` o en las variables de entorno si sus archivos utilizan otras denominaciones.

### 2. Levantar los servicios LLM y TTS

```bash
docker compose build
docker compose up
```

- El servicio LLM expone `http://localhost:8000/v1/chat/completions` y carga automáticamente el modelo indicado en `MODEL_PATH`.
- El servicio TTS expone `http://localhost:8001/synthesize` y transforma texto en audio WAV usando Piper.

Ambos contenedores funcionan completamente offline tras cargar los modelos desde los volúmenes montados.

### 3. Instalar el orquestador local

Cree y active un entorno virtual de Python y luego instale los requisitos:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r orchestrator/requirements.txt
```

### 4. Ejecutar el agente de voz

Con los contenedores corriendo y el entorno activado:

```bash
python orchestrator/main.py --config configs/agent.yaml
```

El orquestador:

1. Captura audio del micrófono a 16 kHz usando `sounddevice`.
2. Detecta segmentos de voz con `webrtcvad` y evita enviar silencio al STT.
3. Transcribe cada segmento con Whisper (`faster-whisper`).
4. Añade el mensaje a la conversación y consulta al LLM local por una respuesta.
5. Solicita al servicio TTS la síntesis de la respuesta y la reproduce por los altavoces.

La configuración por defecto responde en español de forma breve. Puede editar `configs/agent.yaml` para ajustar el prompt del sistema, parámetros del modelo, rutas y comportamiento de reproducción.

### 5. Finalizar

Presione `Ctrl+C` para detener el orquestador. Para apagar los contenedores utilice `docker compose down`.

## Personalización y mejoras

- Cambie el modelo LLM ajustando `MODEL_PATH` y los recursos asignados (`N_THREADS`, `GPU_LAYERS`).
- Use otra voz de Piper modificando las variables `VOICE_MODEL` y `VOICE_CONFIG` o el archivo de configuración.
- Ajuste la sensibilidad del VAD mediante `vad_aggressiveness`, `frame_duration_ms` y `padding_duration_ms`.
- Para mantener memoria de conversaciones largas puede aumentar `max_tokens` o resetear `self.history` en el orquestador según se necesite.

## Licencia

El código del repositorio se publica sin restricciones adicionales. Revise las licencias de cada modelo descargado antes de su uso.
