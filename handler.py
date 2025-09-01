import base64
import os
import random
import tempfile

from dia.model import Dia
import numpy as np
import runpod
import soundfile as sf
import torch
from pydantic import BaseModel, Field
from pydub import AudioSegment




# Global model variable

MODEL_NAME = os.getenv("MODEL_NAME", "nari-labs/Dia-1.6B-0626")
# MODEL_NAME = os.getenv("MODEL_NAME", "nari-labs/Dia-1.6B")
COMPUTE_DTYPE = os.getenv("COMPUTE_DTYPE", "float16")


class TextToSpeechInput(BaseModel):
    text: str
    audio_prompt: str|None = None  # base64 encoded audio prompt
    audio_prompt_text_input: str = ""

    max_new_tokens: int = Field(4072, ge=860, le=4072, description="Upper bound on generated audio length")
    cfg_scale: float = Field(3.0, ge=1.0, le=5.0, description="higher = closer to the prompt.")
    temperature: float = Field(1.3, ge=1.0, le=1.5, description="Sampling temperature; lower = more deterministic.")
    top_p: float = Field(0.95, ge=0.80, le=1.0, description="Nucleus‑sampling probability mass.")
    cfg_filter_top_k: int = Field(30, ge=15, le=50, description="Top‑k filter applied during CFG guidance.")
    speed_factor: float = Field(0.94, ge=0.8, le=1.0, description="Playback‑speed. 1.0 = original.")
    seed: int | None = None
    format: str = "mp3"


DIA_MODEL: Dia | None = None


def load_model() -> Dia:
    global DIA_MODEL
    if DIA_MODEL is None:
        print("Loading Dia model...")

        DIA_MODEL = Dia.from_pretrained(MODEL_NAME, compute_dtype=COMPUTE_DTYPE, device="cuda")
        print("Model loaded successfully")

    return DIA_MODEL


def set_seed(seed: int | None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def handler(event):
    """RunPod serverless handler"""
    try:
        dia_model = load_model()

        job_input = TextToSpeechInput(**event.get("input", {}))

        if not job_input.text:
            return {"error": "No text provided"}

        # Add speaker tags if missing
        if "[S1]" not in job_input.text and "[S2]" not in job_input.text:
            job_input.text = f"[S1] {job_input.text}"

        if job_input.max_new_tokens is None:
            job_input.max_new_tokens = dia_model.config.decoder_config.max_position_embeddings

        print(f"Generating: {job_input.text[:100]}...")

        # Set seed if provided
        seed = job_input.seed
        if seed is not None:
            set_seed(seed)

        # Generate audio
        with torch.inference_mode():
            audio = dia_model.generate(job_input.text)

        output_format = job_input.format

        # Convert to requested format
        with tempfile.NamedTemporaryFile(suffix=f".{output_format}", delete=False) as tmp_file:
            if output_format.lower() == "wav":
                sf.write(tmp_file.name, audio, 44100, format="WAV")
            else:
                # Convert to MP3
                wav_file = tmp_file.name.replace(".mp3", ".wav")
                sf.write(wav_file, audio, 44100)
                audio_segment = AudioSegment.from_wav(wav_file)
                audio_segment.export(tmp_file.name, format="mp3", bitrate="128k")
                os.unlink(wav_file)  # Clean up temp wav file

            # Read file as bytes
            with open(tmp_file.name, "rb") as f:
                audio_data = f.read()

            # Clean up temp file
            os.unlink(tmp_file.name)

        # Calculate duration
        duration = len(audio) / 44100

        return {
            "success": True,
            "audio_base64": base64.b64encode(audio_data).decode(),
            "duration_seconds": round(duration, 2),
            "sample_rate": 44100,
            "format": output_format,
            "file_size_bytes": len(audio_data),
            "text_length": len(job_input.text),
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return {"success": False, "error": str(e)}


runpod.serverless.start({"handler": handler})
