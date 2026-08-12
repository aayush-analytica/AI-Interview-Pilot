import whisper
import os

# Load model once at startup (or lazily)
model = whisper.load_model("base")

def transcribe_audio(file_path: str) -> str:
    """Transcribes audio file using local Whisper model."""
    result = model.transcribe(file_path)
    return result["text"]
