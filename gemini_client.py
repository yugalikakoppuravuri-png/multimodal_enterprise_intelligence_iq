"""
Google Gemini Multimodal Client
Uses official google-genai SDK for multi-modal reasoning across text, documents, and images.
"""

import os
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types


class GeminiMultimodalClient:
    """Invokes Google Gemini models with multimodal context."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = model
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def is_configured(self) -> bool:
        return bool(self.api_key and self.client)

    def generate_response(
        self,
        prompt: str,
        system_instruction: str = "",
        images: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Calls Gemini with prompt, system instruction, and optional image parts.
        images: list of dicts with 'bytes' and 'mime_type'.
        """
        if not self.is_configured():
            raise RuntimeError("Gemini API key is not configured. Please supply an API key.")

        contents = []

        # Add images if provided
        if images:
            for img in images:
                img_bytes = img.get("bytes")
                mime_type = img.get("mime_type", "image/png")
                if img_bytes:
                    contents.append(
                        types.Part.from_bytes(
                            data=img_bytes,
                            mime_type=mime_type
                        )
                    )

        # Add text prompt
        contents.append(prompt)

        config = types.GenerateContentConfig(
            system_instruction=system_instruction if system_instruction else None,
            temperature=0.2
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config
        )

        return response.text
