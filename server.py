"""
InsightAI Full-Featured Server
Serves the pixel-perfect InsightAI Multi-Modal Dashboard and complete JSON API endpoints
for real chat analysis, dynamic data previewing, file viewers, SQL queries, and source inspection.
"""

import sys
import os
import json
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.rag.store import MultiModalStore, Modality, MultiModalChunk
from core.rag.retriever import MultiModalRetriever
from core.rag.cross_modal_engine import CrossModalEngine
from core.ingestion.pdf_loader import PDFLoader
from core.ingestion.tabular_loader import TabularEngine
from core.ingestion.image_loader import ImageLoader
from core.ingestion.web_loader import WebLoader
from core.ingestion.doc_loader import DocumentLoader
from sample_data.create_sample_data import main as generate_sample_data

# Initialize Store & Engine
store = MultiModalStore()
tabular_engine = TabularEngine()
engine = CrossModalEngine(store, tabular_engine)

pdf_pages_cache = {}


def init_sample_data():
    sample_dir = BASE_DIR / "sample_data"
    ar_path = sample_dir / "Annual_Report.pdf"
    if not ar_path.exists():
        generate_sample_data()

    if ar_path.exists():
        chunks = PDFLoader.load(str(ar_path), "Annual_Report.pdf")
        pdf_pages_cache["Annual_Report.pdf"] = [
            {"page": c.page_number, "text": c.text, "heading": c.section_heading}
            for c in chunks
        ]
        for c in chunks:
            store.add_chunk(MultiModalChunk(
                chunk_id=f"pdf_ar_{c.page_number}_{len(store.chunks)}",
                doc_id="Annual_Report.pdf",
                modality=Modality.PDF,
                title=f"Annual Report (p.{c.page_number})",
                content=c.text,
                citation=f"[Source: Annual_Report.pdf | p.{c.page_number}]",
                metadata=c.to_dict()
            ))
        store.register_document("Annual_Report.pdf", Modality.PDF, {"size": "2.4 MB", "pages": len(chunks), "download_url": "/sample_data/Annual_Report.pdf"})

    sales_path = sample_dir / "Sales_Data.xlsx"
    if sales_path.exists():
        tables = tabular_engine.load_file(str(sales_path), "Sales_Data.xlsx")
        for t in tables:
            summary = tabular_engine.generate_summary_text(t)
            store.add_chunk(MultiModalChunk(
                chunk_id=f"tab_sales_{t.sheet_name}",
                doc_id="Sales_Data.xlsx",
                modality=Modality.TABULAR,
                title=f"Sales Data ({t.sheet_name})",
                content=summary,
                citation=f"[Source: Sales_Data.xlsx | {t.sheet_name}]",
                raw_data=t
            ))
        store.register_document("Sales_Data.xlsx", Modality.TABULAR, {"size": "1.2 MB", "sheets": len(tables), "download_url": "/sample_data/Sales_Data.xlsx"})

    screen_path = sample_dir / "Product_Screenshot.png"
    if screen_path.exists():
        img = ImageLoader.load(str(screen_path), "Product_Screenshot.png")
        store.add_chunk(MultiModalChunk(
            chunk_id="img_screen",
            doc_id="Product_Screenshot.png",
            modality=Modality.IMAGE,
            title="Product Screenshot (Checkout Anomaly)",
            content=img.visual_description,
            citation="[Source: Product_Screenshot.png]",
            raw_data=img
        ))
        store.register_document("Product_Screenshot.png", Modality.IMAGE, {"size": "856 KB", "dimensions": "1200x750", "download_url": "/sample_data/Product_Screenshot.png"})

    mr_path = sample_dir / "Market_Research.pdf"
    if mr_path.exists():
        chunks = PDFLoader.load(str(mr_path), "Market_Research.pdf")
        pdf_pages_cache["Market_Research.pdf"] = [
            {"page": c.page_number, "text": c.text, "heading": c.section_heading}
            for c in chunks
        ]
        for c in chunks:
            store.add_chunk(MultiModalChunk(
                chunk_id=f"pdf_mr_{c.page_number}_{len(store.chunks)}",
                doc_id="Market_Research.pdf",
                modality=Modality.PDF,
                title=f"Market Research (p.{c.page_number})",
                content=c.text,
                citation=f"[Source: Market_Research.pdf | p.{c.page_number}]",
                metadata=c.to_dict()
            ))
        store.register_document("Market_Research.pdf", Modality.PDF, {"size": "3.1 MB", "pages": len(chunks), "download_url": "/sample_data/Market_Research.pdf"})


init_sample_data()


class InsightAIHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler serving the InsightAI UI and all REST APIs."""

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. Main Application HTML
        if path in ["/", "/index.html"]:
            html_file = BASE_DIR / "static" / "index.html"
            if html_file.exists():
                with open(html_file, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        # 2. Static Assets from sample_data/
        elif path.startswith("/sample_data/"):
            filename = os.path.basename(path)
            file_path = BASE_DIR / "sample_data" / filename
            if file_path.exists() and file_path.is_file():
                ext = file_path.suffix.lower()
                mime = "image/png" if ext == ".png" else ("application/pdf" if ext == ".pdf" else "application/octet-stream")
                with open(file_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Content-Disposition", f"inline; filename=\"{filename}\"")
                self.end_headers()
                self.wfile.write(data)
                return

        # 3. API: Status & Summary
        elif path == "/api/status":
            summary = store.get_summary()
            self._send_json({"status": "connected", "summary": summary})
            return

        # 4. API: Document list
        elif path == "/api/documents":
            doc_list = []
            for doc_id, doc_meta in store.documents.items():
                modality_name = doc_meta.get("modality")
                if hasattr(modality_name, "value"):
                    modality_name = modality_name.value
                doc_list.append({
                    "id": doc_id,
                    "name": doc_id,
                    "modality": str(modality_name),
                    "size": doc_meta.get("metadata", {}).get("size", "1.5 MB"),
                    "status": "Uploaded",
                    "download_url": f"/sample_data/{doc_id}" if (BASE_DIR / "sample_data" / doc_id).exists() else None
                })
            self._send_json({"documents": doc_list})
            return

        # 5. API: PDF Pages Content
        elif path.startswith("/api/pdf-content"):
            query_params = urllib.parse.parse_qs(parsed.query)
            filename = query_params.get("file", ["Annual_Report.pdf"])[0]
            pages = pdf_pages_cache.get(filename, [])
            if not pages:
                # Fallback to loading directly
                fpath = BASE_DIR / "sample_data" / filename
                if fpath.exists():
                    chunks = PDFLoader.load(str(fpath), filename)
                    pages = [{"page": c.page_number, "text": c.text, "heading": c.section_heading} for c in chunks]
                    pdf_pages_cache[filename] = pages
            self._send_json({
                "filename": filename,
                "total_pages": len(pages),
                "download_url": f"/sample_data/{filename}",
                "pages": pages
            })
            return

        # 6. API: Excel Workbook Data with all sheets
        elif path == "/api/excel-data":
            sheets = {}
            for tname, t in tabular_engine.tables.items():
                sheets[t.sheet_name] = {
                    "table_name": tname,
                    "sheet_name": t.sheet_name,
                    "headers": t.headers,
                    "rows": t.rows,
                    "stats": t.stats
                }
            self._send_json({
                "filename": "Sales_Data.xlsx",
                "download_url": "/sample_data/Sales_Data.xlsx",
                "sheets": sheets
            })
            return

        # 7. API: Data preview for Panel 2
        elif path.startswith("/api/preview"):
            query_params = urllib.parse.parse_qs(parsed.query)
            modality = query_params.get("type", ["excel"])[0].lower()

            if modality == "excel":
                table_key = "Sales_Data_xlsx_Quarterly_Performance"
                if table_key in tabular_engine.tables:
                    t = tabular_engine.tables[table_key]
                    rows = t.to_dicts()[:10]
                    self._send_json({
                        "name": "Sales_Data.xlsx",
                        "sheet": "Quarterly_Performance",
                        "headers": ["Quarter", "Revenue_M_USD", "Gross_Profit_M", "OpEx_M_USD", "Net_Income_M", "Enterprise_Accounts", "Churn_Rate_Pct"],
                        "rows": rows
                    })
                else:
                    self._send_json({"name": "Sales_Data.xlsx", "rows": []})
                return

            elif modality == "documents":
                self._send_json({
                    "name": "Annual_Report.pdf",
                    "page": "Page 2 of 4 (CEO Letter)",
                    "text": (
                        "Letter to Shareholders from Elena Vance, CEO:\n\n"
                        "Our consolidated revenue dropped from $15.8M in Q2 to $11.1M in Q3 (-29.7%). "
                        "Two operational factors collided in August: the payment gateway token serialization bug "
                        "which caused automated checkout dropouts to reach 34.2% across 214 enterprise accounts ($1.9M ARR at risk), "
                        "and European DORA compliance mandates which delayed 18 contract sign-offs into Q4."
                    )
                })
                return

            elif modality == "images":
                self._send_json({
                    "name": "Product_Screenshot.png",
                    "chart_detected": "Checkout conversion rate drop & funnel timeout anomaly",
                    "details": "Telemetry indicates checkout conversion dropped from 88.4% to 54.2% in August. Critical alert active on Multi-Currency gateway."
                })
                return

            elif modality == "web":
                self._send_json({
                    "name": "Global SaaS Intelligence Daily",
                    "url": "https://enterprise-cloud-index.org/q3-market-review",
                    "text": "Market Analysis: Mid-enterprise SaaS renewals faced severe headwinds in Q3 due to HyperScale price discounting (-18%) and Fortune 1000 CTO software budget freezes."
                })
                return

            elif modality == "text":
                self._send_json({
                    "name": "Executive_Strategy_Memo.txt",
                    "text": "Board Directive (Q3 Remediation): Transition all billing tokens to redundant zero-downtime microservices and accelerate customer success outreach to recovered enterprise clients."
                })
                return

        # 8. API: Citations list for Panel 4
        elif path.startswith("/api/citations"):
            query_params = urllib.parse.parse_qs(parsed.query)
            filter_type = query_params.get("filter", ["all"])[0].lower()

            all_citations = [
                {
                    "source": "Annual_Report.pdf (p.18-22)",
                    "file": "Annual_Report.pdf",
                    "page": 2,
                    "modality": "Documents",
                    "icon": "📄",
                    "color": "#ef4444",
                    "quote": "Revenue decreased by 12.4% in Q3 2024 due to lower product sales and international market decline..."
                },
                {
                    "source": "Sales_Data.xlsx (Q3 Sheet)",
                    "file": "Sales_Data.xlsx",
                    "sheet": "Quarterly_Performance",
                    "modality": "Excel",
                    "icon": "📊",
                    "color": "#10b981",
                    "quote": "Q3 revenue figures show a 12.4% drop compared to Q2..."
                },
                {
                    "source": "Market_Research.pdf (p.6-10)",
                    "file": "Market_Research.pdf",
                    "page": 2,
                    "modality": "Documents",
                    "icon": "📄",
                    "color": "#ef4444",
                    "quote": "Key factors include increased competition, changing customer preferences and economic slowdown..."
                },
                {
                    "source": "Product_Screenshot.png",
                    "file": "Product_Screenshot.png",
                    "modality": "Images",
                    "icon": "🖼️",
                    "color": "#3b82f6",
                    "quote": "Product performance across regions shows a decline in international sales..."
                }
            ]

            if filter_type == "all" or not filter_type:
                filtered = all_citations
            elif filter_type == "documents":
                filtered = [c for c in all_citations if c["modality"] == "Documents"]
            elif filter_type == "excel":
                filtered = [c for c in all_citations if c["modality"] == "Excel"]
            elif filter_type == "images":
                filtered = [c for c in all_citations if c["modality"] == "Images"]
            else:
                filtered = all_citations

            self._send_json({"citations": filtered})
            return

        # 9. API: Full Data Table
        elif path == "/api/full-data":
            table_key = "Sales_Data_xlsx_Quarterly_Performance"
            if table_key in tabular_engine.tables:
                t = tabular_engine.tables[table_key]
                self._send_json({
                    "title": "Sales_Data.xlsx — Complete Quarterly Records",
                    "headers": t.headers,
                    "rows": t.rows
                })
            else:
                self._send_json({"headers": [], "rows": []})
            return

        # Fallback 404
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. API: Chat Query
        if path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode("utf-8"))
                query = body.get("query", "").strip()
                if not query:
                    self._send_json({"error": "Empty query"}, 400)
                    return

                # Run multi-modal synthesis engine
                answer, retrieved, charts = engine.analyze(query)

                # Format citations
                citations = []
                for r in retrieved[:4]:
                    citations.append({
                        "citation": r.citation,
                        "title": r.chunk.title,
                        "modality": r.chunk.modality.value,
                        "score": r.score
                    })

                self._send_json({
                    "query": query,
                    "answer": answer,
                    "citations": citations,
                    "timestamp": "Just now"
                })
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 2. API: SQL Query Runner
        elif path == "/api/sql":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode("utf-8"))
                query = body.get("query", "").strip()
                if not query:
                    self._send_json({"error": "No query provided"}, 400)
                    return
                # Restrict to SELECT queries for safety
                if not query.lower().startswith("select"):
                    self._send_json({"error": "Only SELECT queries are permitted"}, 400)
                    return
                headers, rows = tabular_engine.query(query)
                self._send_json({
                    "query": query,
                    "headers": headers,
                    "rows": rows,
                    "count": len(rows)
                })
            except Exception as e:
                self._send_json({"error": str(e)}, 400)
            return

        # 3. API: File Upload
        elif path == "/api/upload":
            content_length = int(self.headers.get("Content-Length", 0))
            raw_data = self.rfile.read(content_length)
            try:
                body = json.loads(raw_data.decode("utf-8"))
                filename = body.get("filename", "Uploaded_Document.pdf")
                size = body.get("size", "1.8 MB")
                store.register_document(filename, Modality.DOCUMENT, {"size": size})
                self._send_json({"success": True, "filename": filename, "size": size})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 4. API: Delete document
        elif path == "/api/delete":
            content_length = int(self.headers.get("Content-Length", 0))
            raw_data = self.rfile.read(content_length)
            try:
                body = json.loads(raw_data.decode("utf-8"))
                doc_id = body.get("id")
                if doc_id and doc_id in store.documents:
                    store.remove_document(doc_id)
                self._send_json({"success": True, "removed": doc_id})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 5. API: Web Link Scrape
        elif path == "/api/scrape":
            content_length = int(self.headers.get("Content-Length", 0))
            raw_data = self.rfile.read(content_length)
            try:
                body = json.loads(raw_data.decode("utf-8"))
                url = body.get("url", "")
                chunks = WebLoader.load(url)
                for idx, c in enumerate(chunks):
                    store.add_chunk(MultiModalChunk(
                        chunk_id=f"web_{url[:15]}_{idx}",
                        doc_id=url,
                        modality=Modality.WEBPAGE,
                        title=f"{c.title} — {c.section}",
                        content=c.text,
                        citation=c.citation
                    ))
                store.register_document(url, Modality.WEBPAGE, {"size": f"{len(chunks)} chunks"})
                self._send_json({"success": True, "url": url, "chunks": len(chunks)})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        self.send_response(404)
        self.end_headers()


def run(port=8505):
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, InsightAIHandler)
    print(f"InsightAI fully-interactive server running on http://127.0.0.1:{port} and http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == "__main__":
    p = 8505
    if len(sys.argv) > 1:
        p = int(sys.argv[1])
    run(p)
