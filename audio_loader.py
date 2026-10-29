"""
Voice & Audio Query Loader
Processes voice input, transcribed voice questions, or uploaded audio recordings (.wav, .mp3).
Supports Gemini audio understanding and OpenAI Whisper transcription with offline fallback.
"""

import os
import io
import base64
from typing import Dict, Any, Optional, Union


class VoiceQuery:
    """Represents an ingested voice question or audio note."""
    def __init__(self, filename_or_source: str, transcript: str, audio_bytes: Optional[bytes] = None, duration_sec: float = 0.0):
        self.source = filename_or_source
        self.transcript = transcript
        self.audio_bytes = audio_bytes
        self.duration_sec = duration_sec

    @property
    def citation(self) -> str:
        return f"[Source: Voice Query | '{self.source}']"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "transcript": self.transcript,
            "duration_sec": self.duration_sec,
            "has_audio": self.audio_bytes is not None,
            "citation": self.citation
        }


class AudioLoader:
    """Handles audio parsing and transcription."""

    @staticmethod
    def load_audio(file_input: Union[str, bytes, io.BytesIO], filename: str) -> VoiceQuery:
        """Load audio file and return VoiceQuery object."""
        if isinstance(file_input, (str, os.PathLike)):
            with open(file_input, "rb") as f:
                audio_bytes = f.read()
        elif isinstance(file_input, bytes):
            audio_bytes = file_input
        elif hasattr(file_input, "read"):
            audio_bytes = file_input.read()
        else:
            raise ValueError("Unsupported audio input")

        # Heuristic duration estimate from byte size (approx 16kbps or standard wav/mp3)
        duration_est = round(len(audio_bytes) / 32000, 1)

        # Basic voice query object; transcription can be populated via LLM client
        return VoiceQuery(
            filename_or_source=filename,
            transcript="",  # Will be transcribed via Gemini / Whisper or UI speech-to-text
            audio_bytes=audio_bytes,
            duration_sec=duration_est
        )
