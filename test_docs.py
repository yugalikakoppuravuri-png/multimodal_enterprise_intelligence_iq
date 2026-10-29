"""
Test Web, Doc, and Text loaders
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.ingestion.doc_loader import DocumentLoader


def test_docs():
    # Test plain text
    sample_text = (
        "Executive Strategy Memo: Q4 Initiatives\n\n"
        "1. Cloud Architecture Hardening\n"
        "We are transitioning all payment token infrastructure to redundant multi-region clusters.\n\n"
        "2. Competitive AI Strategy\n"
        "We are packaging generative intelligence tools into the core subscription."
    )
    chunks = DocumentLoader.load(sample_text, "Executive_Memo.txt")
    assert len(chunks) >= 1
    print(f"[OK] Plain text loader verified ({len(chunks)} chunks, citation: {chunks[0].citation})")


if __name__ == "__main__":
    test_docs()
