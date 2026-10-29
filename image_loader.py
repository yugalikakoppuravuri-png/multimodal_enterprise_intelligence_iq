"""
Image & Vision Loader
Loads visual assets (diagrams, charts, screenshots), extracts visual metadata,
prepares multimodal payloads for Gemini Vision / GPT-4o, and provides
heuristic visual descriptions for offline execution.
"""

import os
import io
import base64
from typing import Dict, Any, Optional, Tuple, Union
from PIL import Image


class ImageAsset:
    """Represents an ingested image, chart, or screenshot."""
    def __init__(self, filename: str, image_bytes: bytes, pil_image: Image.Image, visual_description: str = ""):
        self.filename = filename
        self.image_bytes = image_bytes
        self.pil_image = pil_image
        self.width, self.height = pil_image.size
        self.format = pil_image.format or "PNG"
        self.visual_description = visual_description or self._generate_heuristic_description()

    @property
    def base64_data(self) -> str:
        return base64.b64encode(self.image_bytes).decode('utf-8')

    @property
    def mime_type(self) -> str:
        fmt = self.format.lower()
        if fmt in ["jpg", "jpeg"]:
            return "image/jpeg"
        elif fmt == "webp":
            return "image/webp"
        return "image/png"

    @property
    def citation(self) -> str:
        return f"[Source: {self.filename} | Visual Image Evidence]"

    def _generate_heuristic_description(self) -> str:
        """Produce an initial descriptive summary based on image properties and name."""
        name_clean = os.path.splitext(self.filename)[0].replace("_", " ").title()
        aspect_ratio = round(self.width / max(self.height, 1), 2)
        ratio_type = "Landscape / Dashboard" if aspect_ratio > 1.3 else ("Portrait / Document" if aspect_ratio < 0.8 else "Square")
        return (
            f"Image '{self.filename}' ({name_clean}): {ratio_type} image, {self.width}x{self.height}px. "
            f"Visual enterprise artifact containing analytical charts, UI telemetry, or system diagrams."
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "width": self.width,
            "height": self.height,
            "format": self.format,
            "mime_type": self.mime_type,
            "visual_description": self.visual_description,
            "citation": self.citation
        }


class ImageLoader:
    """Loads and inspects image files."""

    @staticmethod
    def load(file_input: Union[str, bytes, io.BytesIO], filename: str) -> ImageAsset:
        """Load image file or bytes into an ImageAsset."""
        if isinstance(file_input, (str, os.PathLike)):
            with open(file_input, "rb") as f:
                img_bytes = f.read()
        elif isinstance(file_input, bytes):
            img_bytes = file_input
        elif hasattr(file_input, "read"):
            img_bytes = file_input.read()
            if isinstance(img_bytes, str):
                img_bytes = img_bytes.encode('latin1')
        else:
            raise ValueError("Unsupported image input type")

        pil_img = Image.open(io.BytesIO(img_bytes))
        # Ensure image is loaded into memory
        pil_img.load()

        return ImageAsset(
            filename=filename,
            image_bytes=img_bytes,
            pil_image=pil_img
        )
