"""
Configuration & Constants for Multi-Modal Enterprise Intelligence Assistant
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.resolve()
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
STATIC_DIR = BASE_DIR / "static"

# Supported Modalities and File Extensions
SUPPORTED_EXTENSIONS = {
    "pdf": [".pdf"],
    "tabular": [".xlsx", ".xls", ".csv"],
    "image": [".png", ".jpg", ".jpeg", ".webp"],
    "document": [".docx", ".txt", ".md"],
    "audio": [".wav", ".mp3", ".m4a"]
}

ALL_ALLOWED_EXTENSIONS = [
    ext for sublist in SUPPORTED_EXTENSIONS.values() for ext in sublist
]

# LLM Providers & Models
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]

DEFAULT_OPENAI_MODEL = "gpt-4o"
OPENAI_MODELS = ["gpt-4o", "gpt-4o-mini"]

# RAG Defaults
DEFAULT_TOP_K = 6
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

# UI Settings
APP_TITLE = "Enterprise Multi-Modal Intelligence & Research Assistant"
APP_SUBTITLE = "Cross-Modal RAG • Quantitative Data Analytics • Vision Telemetry • Evidence-Based Reasoning"
