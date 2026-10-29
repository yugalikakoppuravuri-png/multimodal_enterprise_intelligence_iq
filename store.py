"""
Multi-Modal Knowledge Store
Unified in-memory repository for storing, categorizing, and indexing chunks
across all enterprise modalities (PDF, Excel, Images, Web, Audio, Docs).
"""

from enum import Enum
from typing import Dict, List, Any, Optional
import time


class Modality(str, Enum):
    PDF = "PDF"
    TABULAR = "Excel / CSV"
    IMAGE = "Image / Chart"
    WEBPAGE = "Web Page"
    DOCUMENT = "Document"
    VOICE = "Voice Query"


class MultiModalChunk:
    """Unified chunk representation across all media types."""
    def __init__(
        self,
        chunk_id: str,
        doc_id: str,
        modality: Modality,
        title: str,
        content: str,
        citation: str,
        metadata: Optional[Dict[str, Any]] = None,
        raw_data: Optional[Any] = None
    ):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.modality = modality
        self.title = title
        self.content = content
        self.citation = citation
        self.metadata = metadata or {}
        self.raw_data = raw_data  # TabularData, ImageAsset, etc.
        self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "modality": self.modality.value,
            "title": self.title,
            "content": self.content[:300] + ("..." if len(self.content) > 300 else ""),
            "full_content_length": len(self.content),
            "citation": self.citation,
            "metadata": self.metadata
        }


class MultiModalStore:
    """Stores all indexed chunks and provides lookup and filtering."""
    def __init__(self):
        self.chunks: List[MultiModalChunk] = []
        self.documents: Dict[str, Dict[str, Any]] = {}

    def add_chunk(self, chunk: MultiModalChunk):
        self.chunks.append(chunk)

    def register_document(self, doc_id: str, modality: Modality, meta: Optional[Dict[str, Any]] = None):
        self.documents[doc_id] = {
            "doc_id": doc_id,
            "modality": modality.value,
            "added_at": time.time(),
            "metadata": meta or {}
        }

    def remove_document(self, doc_id: str):
        self.chunks = [c for c in self.chunks if c.doc_id != doc_id]
        if doc_id in self.documents:
            del self.documents[doc_id]

    def clear(self):
        self.chunks.clear()
        self.documents.clear()

    def get_by_modality(self, modality: Modality) -> List[MultiModalChunk]:
        return [c for c in self.chunks if c.modality == modality]

    def get_summary(self) -> Dict[str, Any]:
        """Returns statistics on the store's current inventory."""
        modality_counts: Dict[str, int] = {}
        for c in self.chunks:
            mod_val = c.modality.value
            modality_counts[mod_val] = modality_counts.get(mod_val, 0) + 1

        total_words = sum(len(c.content.split()) for c in self.chunks)

        return {
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunks),
            "estimated_tokens": int(total_words * 1.3),
            "modality_breakdown": modality_counts,
            "document_list": list(self.documents.values())
        }
