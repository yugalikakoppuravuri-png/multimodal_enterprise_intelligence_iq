"""
Multi-Modal Hybrid Retriever
Ranks and retrieves cross-modal chunks using BM25-style lexical scoring,
modality intent classification, and cross-modality diversification.
"""

import re
import math
from typing import List, Dict, Any, Set, Tuple
from .store import MultiModalStore, MultiModalChunk, Modality


class RetrievalResult:
    """Represents a retrieved chunk with its computed score and relevance explanation."""
    def __init__(self, chunk: MultiModalChunk, score: float, matched_terms: List[str]):
        self.chunk = chunk
        self.score = round(score, 4)
        self.matched_terms = matched_terms

    @property
    def citation(self) -> str:
        return self.chunk.citation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk.chunk_id,
            "doc_id": self.chunk.doc_id,
            "modality": self.chunk.modality.value,
            "title": self.chunk.title,
            "score": self.score,
            "matched_terms": self.matched_terms,
            "citation": self.citation,
            "content": self.chunk.content
        }


class MultiModalRetriever:
    """Retrieves relevant chunks across multiple modalities."""
    def __init__(self, store: MultiModalStore):
        self.store = store

    def _tokenize(self, text: str) -> List[str]:
        """Normalize and tokenize text into keywords."""
        words = re.findall(r'[a-zA-Z0-9_\-\$]+', text.lower())
        stopwords = {
            "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
            "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
            "to", "was", "were", "will", "with", "our", "we", "what", "why",
            "did", "do", "does", "how", "can", "could", "should", "would"
        }
        return [w for w in words if w not in stopwords and len(w) > 1]

    def _detect_modality_intent(self, query: str) -> Dict[Modality, float]:
        """Detect what modalities are most relevant to the query to apply dynamic boosting."""
        q_lower = query.lower()
        boosts = {
            Modality.PDF: 1.0,
            Modality.TABULAR: 1.0,
            Modality.IMAGE: 1.0,
            Modality.WEBPAGE: 1.0,
            Modality.DOCUMENT: 1.0,
            Modality.VOICE: 1.0
        }

        # Tabular / Quantitative signals
        if any(w in q_lower for w in ["revenue", "sales", "quarter", "q1", "q2", "q3", "q4", "growth", "margin", "finance", "data", "excel", "numbers", "drop", "increase", "decrease", "metric"]):
            boosts[Modality.TABULAR] += 1.8

        # Market / External research signals
        if any(w in q_lower for w in ["market", "competitor", "industry", "external", "macro", "factor", "research", "report", "economy", "inflation", "trend"]):
            boosts[Modality.PDF] += 1.4
            boosts[Modality.WEBPAGE] += 1.3

        # Visual signals
        if any(w in q_lower for w in ["chart", "screenshot", "diagram", "image", "ui", "visual", "dashboard", "funnel", "spike", "drop off"]):
            boosts[Modality.IMAGE] += 2.0

        # General PDF / Report signals
        if any(w in q_lower for w in ["annual report", "policy", "memo", "letter", "management", "strategy"]):
            boosts[Modality.PDF] += 1.5

        return boosts

    def retrieve(self, query: str, top_k: int = 8, ensure_cross_modal: bool = True) -> List[RetrievalResult]:
        """
        Execute hybrid search across all indexed chunks.
        If ensure_cross_modal is True, guarantees at least 1 top result from every
        relevant modality present in the store.
        """
        if not self.store.chunks:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            query_tokens = query.lower().split()

        query_set = set(query_tokens)
        modality_boosts = self._detect_modality_intent(query)

        # Compute document frequencies for IDF
        doc_freq: Dict[str, int] = {}
        total_chunks = len(self.store.chunks)
        for chunk in self.store.chunks:
            chunk_tokens = set(self._tokenize(chunk.title + " " + chunk.content))
            for t in query_set:
                if t in chunk_tokens:
                    doc_freq[t] = doc_freq.get(t, 0) + 1

        results = []
        for chunk in self.store.chunks:
            chunk_tokens = self._tokenize(chunk.title + " " + chunk.content)
            chunk_token_counts: Dict[str, int] = {}
            for t in chunk_tokens:
                chunk_token_counts[t] = chunk_token_counts.get(t, 0) + 1

            matched_terms = []
            bm25_score = 0.0
            doc_len = len(chunk_tokens)
            avg_doc_len = 150.0  # approximate average length
            k1 = 1.2
            b = 0.75

            for t in query_set:
                if t in chunk_token_counts:
                    matched_terms.append(t)
                    tf = chunk_token_counts[t]
                    df = doc_freq.get(t, 1)
                    idf = math.log((total_chunks - df + 0.5) / (df + 0.5) + 1.0)
                    term_score = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / avg_doc_len))))
                    bm25_score += term_score

            # Title exact substring bonus
            for t in query_set:
                if t in chunk.title.lower():
                    bm25_score += 2.0
                if t in chunk.doc_id.lower():
                    bm25_score += 1.5

            # Apply modality boost
            boost = modality_boosts.get(chunk.modality, 1.0)
            final_score = bm25_score * boost

            if final_score > 0.05 or len(matched_terms) > 0:
                results.append(RetrievalResult(chunk=chunk, score=final_score, matched_terms=matched_terms))

        # Sort descending by score
        results.sort(key=lambda r: r.score, reverse=True)

        if not ensure_cross_modal or len(results) <= top_k:
            return results[:top_k]

        # Cross-modal balancing: collect top results while ensuring diverse modalities
        selected: List[RetrievalResult] = []
        selected_modalities: Set[Modality] = set()

        # Group by modality
        by_modality: Dict[Modality, List[RetrievalResult]] = {}
        for r in results:
            m = r.chunk.modality
            if m not in by_modality:
                by_modality[m] = []
            by_modality[m].append(r)

        # Pick the #1 chunk from each active modality if score is respectable
        for m, mod_results in by_modality.items():
            if mod_results and mod_results[0].score > 0.1:
                selected.append(mod_results[0])
                selected_modalities.add(m)

        # Fill remaining slots with the highest overall scoring chunks
        for r in results:
            if len(selected) >= top_k:
                break
            if r not in selected:
                selected.append(r)

        # Re-sort selected chunks by score
        selected.sort(key=lambda r: r.score, reverse=True)
        return selected[:top_k]
