"""
OpenAI Multimodal Client
Uses OpenAI API (GPT-4o / GPT-4o-mini) for text and vision cross-modal reasoning.
"""

import os
from typing import List, Dict, Any, Optional
from openai import OpenAI


class OpenAIMultimodalClient:
    """Invokes OpenAI GPT-4o with multimodal context."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def is_configured(self) -> bool:
        return bool(self.api_key and self.client)

    def generate_response(
        self,
        prompt: str,
        system_instruction: str = "",
        images: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Calls OpenAI with prompt, system instruction, and optional images.
        images: list of dicts with 'base64' and 'mime_type'.
        """
        if not self.is_configured():
            raise RuntimeError("OpenAI API key is not configured. Please supply an API key.")

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        user_content = []
        user_content.append({"type": "text", "text": prompt})

        if images:
            for img in images:
                b64 = img.get("base64")
                mime = img.get("mime_type", "image/png")
                if b64:
                    user_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{b64}"
                        }
                    })

        messages.append({"role": "user", "content": user_content})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.2
        )

        return response.choices[0].message.content
