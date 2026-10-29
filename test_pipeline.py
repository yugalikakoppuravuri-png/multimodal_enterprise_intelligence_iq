"""
Automated End-to-End Pipeline Verification Test
Verifies ingestion of all modalities, hybrid retrieval, cross-modal reasoning,
citations generation, and Plotly chart generation.
"""

import sys
import os
from pathlib import Path

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.rag.store import MultiModalStore, Modality, MultiModalChunk
from core.rag.retriever import MultiModalRetriever
from core.rag.cross_modal_engine import CrossModalEngine
from core.ingestion.pdf_loader import PDFLoader
from core.ingestion.tabular_loader import TabularEngine
from core.ingestion.image_loader import ImageLoader
from core.visualization.chart_generator import EnterpriseChartGenerator
from sample_data.create_sample_data import main as generate_sample_data


def test_pipeline():
    print("==================================================")
    print("RUNNING MULTI-MODAL ENTERPRISE RAG PIPELINE TESTS")
    print("==================================================")

    sample_dir = BASE_DIR / "sample_data"
    annual_report_path = sample_dir / "Annual_Report.pdf"
    sales_excel_path = sample_dir / "Sales_Data.xlsx"
    screenshot_path = sample_dir / "Product_Screenshot.png"
    market_research_path = sample_dir / "Market_Research.pdf"

    # 1. Check/Generate sample files
    if not (annual_report_path.exists() and sales_excel_path.exists() and screenshot_path.exists() and market_research_path.exists()):
        print("Sample data missing. Generating sample files...")
        generate_sample_data()

    store = MultiModalStore()
    tabular_engine = TabularEngine()
    engine = CrossModalEngine(store, tabular_engine)

    # 2. Ingest PDF 1: Annual Report
    print("\n[1/5] Ingesting Annual_Report.pdf...")
    pdf_chunks = PDFLoader.load(str(annual_report_path), "Annual_Report.pdf")
    assert len(pdf_chunks) >= 4, f"Expected at least 4 PDF chunks, got {len(pdf_chunks)}"
    for c in pdf_chunks:
        store.add_chunk(MultiModalChunk(
            chunk_id=f"pdf_ar_{c.page_number}",
            doc_id="Annual_Report.pdf",
            modality=Modality.PDF,
            title=f"Annual Report — Page {c.page_number} ({c.section_heading})",
            content=c.text,
            citation=c.citation,
            metadata=c.to_dict()
        ))
    store.register_document("Annual_Report.pdf", Modality.PDF)
    print(f"✓ Annual Report ingested ({len(pdf_chunks)} chunks, page-indexed)")

    # 3. Ingest Excel: Sales_Data.xlsx
    print("\n[2/5] Ingesting Sales_Data.xlsx...")
    tables = tabular_engine.load_file(str(sales_excel_path), "Sales_Data.xlsx")
    assert len(tables) >= 3, f"Expected 3 sheets, got {len(tables)}"
    for t in tables:
        summary_text = tabular_engine.generate_summary_text(t)
        store.add_chunk(MultiModalChunk(
            chunk_id=f"tab_{t.sheet_name}",
            doc_id="Sales_Data.xlsx",
            modality=Modality.TABULAR,
            title=f"Sales Data — Sheet '{t.sheet_name}' ({t.num_rows} rows)",
            content=summary_text,
            citation=f"[Source: Sales_Data.xlsx | Sheet '{t.sheet_name}']",
            metadata={"rows": t.num_rows, "cols": t.num_cols, "sheet": t.sheet_name},
            raw_data=t
        ))
    store.register_document("Sales_Data.xlsx", Modality.TABULAR)
    print(f"✓ Excel data ingested ({len(tables)} sheets registered into SQLite)")

    # Test SQLite query directly
    headers, rows = tabular_engine.query("SELECT Quarter, Revenue_M_USD FROM Sales_Data_xlsx_Quarterly_Performance WHERE Quarter = 'Q3 2024'")
    assert len(rows) == 1 and rows[0][1] == 11.1, f"Expected Q3 Revenue 11.1, got {rows}"
    print(f"✓ SQLite in-memory query verified: Q3 Revenue = ${rows[0][1]}M")

    # 4. Ingest Image: Product_Screenshot.png
    print("\n[3/5] Ingesting Product_Screenshot.png...")
    img_asset = ImageLoader.load(str(screenshot_path), "Product_Screenshot.png")
    assert img_asset.width == 1200 and img_asset.height == 750
    store.add_chunk(MultiModalChunk(
        chunk_id="img_screenshot",
        doc_id="Product_Screenshot.png",
        modality=Modality.IMAGE,
        title="Product Screenshot — Checkout Funnel Alert",
        content=img_asset.visual_description,
        citation=img_asset.citation,
        metadata=img_asset.to_dict(),
        raw_data=img_asset
    ))
    store.register_document("Product_Screenshot.png", Modality.IMAGE)
    print(f"✓ Image telemetry asset ingested ({img_asset.width}x{img_asset.height}px, base64 payload ready)")

    # 5. Ingest PDF 2: Market_Research.pdf
    print("\n[4/5] Ingesting Market_Research.pdf...")
    market_chunks = PDFLoader.load(str(market_research_path), "Market_Research.pdf")
    for c in market_chunks:
        store.add_chunk(MultiModalChunk(
            chunk_id=f"pdf_mr_{c.page_number}",
            doc_id="Market_Research.pdf",
            modality=Modality.PDF,
            title=f"Market Research — Page {c.page_number} ({c.section_heading})",
            content=c.text,
            citation=c.citation,
            metadata=c.to_dict()
        ))
    store.register_document("Market_Research.pdf", Modality.PDF)
    print(f"✓ Market Research PDF ingested ({len(market_chunks)} chunks)")

    # Summary verification
    summary = store.get_summary()
    print("\nMulti-Modal Store Summary:")
    print(f"- Total Documents: {summary['total_documents']}")
    print(f"- Total Chunks: {summary['total_chunks']}")
    print(f"- Modality Breakdown: {summary['modality_breakdown']}")

    # 6. Execute Multi-Modal Query
    query = "Why did our revenue decrease in Q3, and what are the major market factors responsible?"
    print(f"\n[5/5] Executing Cross-Modal Research Query:\n\"{query}\"")

    answer, retrieved, charts = engine.analyze(query)

    print("\n--- RETRIEVED SOURCES & CITATIONS ---")
    for r in retrieved:
        print(f"[{r.chunk.modality.value}] {r.citation} — Score: {r.score}")

    print("\n--- SYNTHESIZED EXECUTIVE ANSWER EXCERPT ---")
    print(answer[:600] + "...\n")

    print(f"✓ Generated {len(charts)} interactive Plotly charts!")
    assert len(charts) >= 3, "Expected 3 generated charts (revenue trend, regional comparison, waterfall)"
    assert len(retrieved) >= 4, "Expected at least 4 cross-modal evidence citations"

    print("\n==================================================")
    print("ALL TESTS PASSED SUCCESSFULLY! 🚀")
    print("==================================================")


if __name__ == "__main__":
    test_pipeline()
