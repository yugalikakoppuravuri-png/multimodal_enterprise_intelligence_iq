"""
PDF Document Loader
Extracts text, metadata, page numbers, and structural sections from PDF documents
for precise page-level enterprise citations.
"""

import os
import io
import re
from typing import List, Dict, Any, Union
from pypdf import PdfReader


class PDFPageChunk:
    """Represents a text chunk from a specific PDF page with metadata."""
    def __init__(self, doc_id: str, page_number: int, total_pages: int, text: str, section_heading: str = ""):
        self.doc_id = doc_id
        self.page_number = page_number
        self.total_pages = total_pages
        self.text = text
        self.section_heading = section_heading

    @property
    def citation(self) -> str:
        return f"[Source: {self.doc_id} | Page {self.page_number} of {self.total_pages}]"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "page_number": self.page_number,
            "total_pages": self.total_pages,
            "text": self.text,
            "section_heading": self.section_heading,
            "citation": self.citation
        }


class PDFLoader:
    """Extracts text and page-indexed chunks from PDF files."""

    @staticmethod
    def load(file_input: Union[str, bytes, io.BytesIO], filename: str, chunk_size: int = 800, overlap: int = 150) -> List[PDFPageChunk]:
        """Parse PDF and return chunked text with exact page numbers."""
        if isinstance(file_input, (str, os.PathLike)):
            reader = PdfReader(file_input)
        elif isinstance(file_input, bytes):
            reader = PdfReader(io.BytesIO(file_input))
        elif hasattr(file_input, "read"):
            data = file_input.read()
            if isinstance(data, bytes):
                reader = PdfReader(io.BytesIO(data))
            else:
                reader = PdfReader(io.BytesIO(data.encode('utf-8', errors='replace')))
        else:
            raise ValueError("Unsupported PDF input type")

        total_pages = len(reader.pages)
        chunks = []

        for page_idx, page in enumerate(reader.pages):
            page_num = page_idx + 1
            raw_text = page.extract_text() or ""
            # Clean text
            cleaned_text = re.sub(r'\r\n|\r', '\n', raw_text)
            cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
            cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text).strip()

            if not cleaned_text:
                continue

            # Detect probable section heading (first non-empty line or capitalized line)
            lines = [l.strip() for l in cleaned_text.split('\n') if l.strip()]
            heading = lines[0] if lines else f"Page {page_num}"
            if len(heading) > 80:
                heading = heading[:77] + "..."

            # If page is short, keep as single chunk
            if len(cleaned_text) <= chunk_size + overlap:
                chunks.append(PDFPageChunk(
                    doc_id=filename,
                    page_number=page_num,
                    total_pages=total_pages,
                    text=cleaned_text,
                    section_heading=heading
                ))
            else:
                # Split with overlap
                start = 0
                sub_idx = 1
                while start < len(cleaned_text):
                    end = start + chunk_size
                    # Try to break at a newline or period
                    if end < len(cleaned_text):
                        split_break = cleaned_text.rfind('\n', start, end)
                        if split_break == -1 or split_break <= start + (chunk_size // 2):
                            split_break = cleaned_text.rfind('. ', start, end)
                        if split_break > start + (chunk_size // 2):
                            end = split_break + 1

                    chunk_text = cleaned_text[start:end].strip()
                    if chunk_text:
                        sub_heading = f"{heading} (Part {sub_idx})" if sub_idx > 1 else heading
                        chunks.append(PDFPageChunk(
                            doc_id=filename,
                            page_number=page_num,
                            total_pages=total_pages,
                            text=chunk_text,
                            section_heading=sub_heading
                        ))
                        sub_idx += 1
                    start += (chunk_size - overlap)

        return chunks
