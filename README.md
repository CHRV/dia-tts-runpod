# dia-tts-runpod

Text-to-Speech (TTS) generation using the Dia model on RunPod

This project provides a Python handler for RunPod serverless deployment, a batch script for generating MP3 files from text, and example usage files. It uses the Dia model (nari-labs/Dia-1.6B) for speech synthesis.

## Features

- Generate synthetic speech from text with customizable parameters (seed, top_p, format, etc.)
- Automatic conversion to MP3 or WAV
- Batch script to process a JSONL file and generate multiple audio files
- GPU-ready Dockerfile (CUDA 12.6)

## Project Structure

```
.
├── Dockerfile
├── handler.py
├── pyproject.toml
├── uv.lock
├── README.md
└── examples/
    ├── input.jsonl
    ├── script.sh
```

## Installation

### 1. Build the Docker container

Make sure you have Docker and a CUDA-compatible GPU.

```bash
docker build -t dia-tts-runpod .
```

### 2. Run the server

```bash
docker run --gpus all -p 8000:8000 dia-tts-runpod
```

## Usage

### API Handler

The `handler.py` file exposes a RunPod-compatible handler for TTS generation. Input parameters include:

- `text`: Text to synthesize (use [S1], [S2] speaker tags for dialogues)
- `format`: "mp3" or "wav"
- `seed`, `top_p`, `cfg_filter_top_k`, etc.: See the `TextToSpeechInput` model in `handler.py`

Example JSON payload:

```json
{
  "input": {
    "text": "[S1] Did you see that documentary about octopuses last night?",
    "format": "mp3",
    "seed": 23,
    "top_p": 0.95,
    "cfg_filter_top_k": 45,
    "max_new_tokens": 4000
  }
}
```

### Batch Script (`examples/script.sh`)

This script reads each line from `input.jsonl`, sends a POST request to the RunPod API, and saves the result as MP3 files.

Set the following environment variables before running:

- `RUNPOD_API_KEY`: Your RunPod API key
- `ENDPOINT_ID`: Your RunPod endpoint ID

Run the script:

```bash
cd examples
bash script.sh
```

Generated MP3 files will be named `1.mp3`, `2.mp3`, etc.

### Example Input (`examples/input.jsonl`)

This file contains example dialogue lines to convert to audio. Each line is a JSON object with input parameters.

## Runpod requirements

- 16 GB+ VRAM
- 30 GB+ Disk space

## Dependencies

- Python 3.10+
- CUDA 12.6
- ffmpeg, libsndfile1
- Python libraries: torch, numpy, soundfile, pydub, pydantic, runpod

Python dependencies are managed via `uv` and `pyproject.toml`.

## Deployment on RunPod

The handler is ready for deployment on RunPod Serverless. Configure your endpoint to use `handler.py`.
