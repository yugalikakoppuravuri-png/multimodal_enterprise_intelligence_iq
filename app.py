"""
InsightAI - Multi-Modal Enterprise Intelligence & Research Assistant
Pixel-Accurate SaaS Executive Dashboard matching the reference design.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go

# Add base directory to path
BASE_DIR = Path(__file__).parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import SAMPLE_DATA_DIR, STATIC_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from core.rag.store import MultiModalStore, Modality, MultiModalChunk
from core.rag.retriever import MultiModalRetriever
from core.rag.cross_modal_engine import CrossModalEngine
from core.ingestion.pdf_loader import PDFLoader
from core.ingestion.tabular_loader import TabularEngine
from core.ingestion.image_loader import ImageLoader
from core.visualization.chart_generator import EnterpriseChartGenerator

# Page Setup
st.set_page_config(
    page_title="InsightAI — Multi-Modal Enterprise Intelligence",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Fidelity CSS to match reference image pixel-for-pixel
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global canvas */
    .stApp {
        background-color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0f172a;
    }
    
    /* Remove default Streamlit top margins */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Top Global Navbar */
    .insight-navbar {
        background-color: #0d1527;
        color: #ffffff;
        padding: 12px 24px;
        margin-left: -2rem;
        margin-right: -2rem;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .brand-section {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-icon {
        background: #2563eb;
        width: 34px;
        height: 34px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 18px;
        color: white;
    }
    .brand-title-wrap {
        display: flex;
        flex-direction: column;
    }
    .brand-title {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
    }
    .brand-sub {
        font-size: 11px;
        color: #94a3b8;
    }
    .navbar-right {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .user-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #f8fafc;
        font-size: 13px;
        font-weight: 500;
    }
    .user-avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #3b82f6;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
    }

    /* Sub-header status bar */
    .status-bar {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding-right: 4px;
        margin-bottom: 10px;
    }
    .connected-tag {
        font-size: 11.5px;
        color: #059669;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .connected-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        display: inline-block;
    }

    /* Sidebar Dark Navigation */
    section[data-testid="stSidebar"] {
        background-color: #0e1424 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        min-width: 240px !important;
    }
    .sidebar-menu-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        border-radius: 8px;
        color: #94a3b8;
        font-size: 13.5px;
        font-weight: 500;
        margin-bottom: 4px;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .sidebar-menu-item:hover {
        background: rgba(255, 255, 255, 0.05);
        color: #f8fafc;
    }
    .sidebar-menu-item.active {
        background: #2563eb;
        color: #ffffff;
        font-weight: 600;
    }
    .sidebar-bottom-card {
        margin-top: 40px;
        padding: 14px;
        border-radius: 10px;
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #94a3b8;
        font-size: 12px;
        line-height: 1.4;
    }

    /* White Dashboard Cards */
    .dash-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
        margin-bottom: 16px;
    }

    /* Welcome Left Card */
    .assistant-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 17px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .assistant-desc {
        font-size: 12.5px;
        color: #64748b;
        margin-bottom: 16px;
        line-height: 1.4;
    }

    /* 6 Modality Grid */
    .modality-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 16px;
    }
    .mod-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        display: flex;
        flex-direction: column;
        transition: all 0.2s ease;
    }
    .mod-card:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .mod-icon-wrap {
        width: 32px;
        height: 32px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 8px;
        font-size: 16px;
    }
    .mod-title {
        font-size: 13px;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 2px;
    }
    .mod-desc {
        font-size: 11px;
        color: #64748b;
        line-height: 1.3;
    }

    /* Upload Box */
    .upload-dropzone {
        border: 1.5px dashed #cbd5e1;
        background: #f8fafc;
        border-radius: 10px;
        padding: 20px 16px;
        text-align: center;
        color: #64748b;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .upload-dropzone:hover {
        border-color: #3b82f6;
        background: #f0f7ff;
    }
    .upload-main-text {
        font-size: 13px;
        font-weight: 600;
        color: #334155;
        margin-top: 6px;
    }
    .upload-sub-text {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 2px;
    }

    /* Right Chat Card */
    .chat-user-msg {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 14px;
    }
    .chat-user-bubble {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e3a8a;
        border-radius: 16px 16px 2px 16px;
        padding: 10px 16px;
        font-size: 13px;
        max-width: 85%;
        line-height: 1.45;
        font-weight: 500;
    }
    .chat-time {
        font-size: 10px;
        color: #94a3b8;
        text-align: right;
        margin-top: 4px;
    }

    .chat-ai-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
    }
    .ai-avatar {
        background: #2563eb;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
    }
    .ai-content {
        font-size: 12.5px;
        color: #334155;
        line-height: 1.55;
        margin-bottom: 12px;
    }
    .ai-content strong {
        color: #0f172a;
    }

    /* Visual Summary in Chat */
    .visual-summary-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 12px;
    }
    .visual-summary-title {
        font-size: 11.5px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Sources Badges Bar */
    .sources-bar {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px;
        font-size: 11px;
        color: #64748b;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid #f1f5f9;
    }
    .source-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 8px;
        border-radius: 6px;
        background: #f1f5f9;
        color: #334155;
        border: 1px solid #e2e8f0;
        font-size: 11px;
        font-weight: 500;
    }

    /* Bottom 4 Panels */
    .panel-header {
        font-size: 14px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 12px;
    }
    .panel-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 14px;
        height: 100%;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
    }

    /* File List Items in Panel 1 */
    .file-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 10px;
        border: 1px solid #f1f5f9;
        border-radius: 8px;
        margin-bottom: 6px;
        background: #fafafa;
        font-size: 12px;
    }
    .file-info {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .file-name {
        font-weight: 600;
        color: #1e293b;
        font-size: 11.5px;
    }
    .file-size {
        font-size: 10.5px;
        color: #94a3b8;
    }
    .upload-status {
        font-size: 11px;
        color: #059669;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Mini Table in Panel 2 */
    .mini-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
        margin-bottom: 12px;
    }
    .mini-table th {
        background: #f8fafc;
        color: #64748b;
        text-align: left;
        padding: 6px 8px;
        border-bottom: 1px solid #e2e8f0;
        font-weight: 600;
    }
    .mini-table td {
        padding: 6px 8px;
        border-bottom: 1px solid #f1f5f9;
        color: #334155;
    }

    /* Citations in Panel 4 */
    .cite-item {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px 10px;
        margin-bottom: 8px;
        font-size: 11.5px;
    }
    .cite-item-header {
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 3px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .cite-item-quote {
        color: #64748b;
        font-size: 11px;
        line-height: 1.35;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "store" not in st.session_state:
    st.session_state.store = MultiModalStore()

if "tabular_engine" not in st.session_state:
    st.session_state.tabular_engine = TabularEngine()

if "cross_modal_engine" not in st.session_state:
    st.session_state.cross_modal_engine = CrossModalEngine(
        st.session_state.store,
        st.session_state.tabular_engine
    )

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Home"


# Pre-load demo dataset if empty
def ensure_case_study_loaded():
    if len(st.session_state.store.chunks) == 0:
        annual_path = SAMPLE_DATA_DIR / "Annual_Report.pdf"
        sales_path = SAMPLE_DATA_DIR / "Sales_Data.xlsx"
        screen_path = SAMPLE_DATA_DIR / "Product_Screenshot.png"
        market_path = SAMPLE_DATA_DIR / "Market_Research.pdf"

        if annual_path.exists():
            chunks = PDFLoader.load(str(annual_path), "Annual_Report.pdf")
            for c in chunks:
                st.session_state.store.add_chunk(MultiModalChunk(
                    chunk_id=f"pdf_ar_{c.page_number}_{len(st.session_state.store.chunks)}",
                    doc_id="Annual_Report.pdf",
                    modality=Modality.PDF,
                    title=f"Annual Report (p.{c.page_number})",
                    content=c.text,
                    citation=f"[Source: Annual_Report.pdf | p.{c.page_number}]",
                    metadata=c.to_dict()
                ))
            st.session_state.store.register_document("Annual_Report.pdf", Modality.PDF)

        if sales_path.exists():
            tables = st.session_state.tabular_engine.load_file(str(sales_path), "Sales_Data.xlsx")
            for t in tables:
                summary_text = st.session_state.tabular_engine.generate_summary_text(t)
                st.session_state.store.add_chunk(MultiModalChunk(
                    chunk_id=f"tab_sales_{t.sheet_name}",
                    doc_id="Sales_Data.xlsx",
                    modality=Modality.TABULAR,
                    title=f"Sales Data ({t.sheet_name})",
                    content=summary_text,
                    citation=f"[Source: Sales_Data.xlsx | {t.sheet_name}]",
                    raw_data=t
                ))
            st.session_state.store.register_document("Sales_Data.xlsx", Modality.TABULAR)

        if screen_path.exists():
            img_asset = ImageLoader.load(str(screen_path), "Product_Screenshot.png")
            st.session_state.store.add_chunk(MultiModalChunk(
                chunk_id="img_screen",
                doc_id="Product_Screenshot.png",
                modality=Modality.IMAGE,
                title="Product Screenshot (Checkout Anomaly)",
                content=img_asset.visual_description,
                citation="[Source: Product_Screenshot.png]",
                raw_data=img_asset
            ))
            st.session_state.store.register_document("Product_Screenshot.png", Modality.IMAGE)

        if market_path.exists():
            chunks = PDFLoader.load(str(market_path), "Market_Research.pdf")
            for c in chunks:
                st.session_state.store.add_chunk(MultiModalChunk(
                    chunk_id=f"pdf_mr_{c.page_number}_{len(st.session_state.store.chunks)}",
                    doc_id="Market_Research.pdf",
                    modality=Modality.PDF,
                    title=f"Market Research (p.{c.page_number})",
                    content=c.text,
                    citation=f"[Source: Market_Research.pdf | p.{c.page_number}]",
                    metadata=c.to_dict()
                ))
            st.session_state.store.register_document("Market_Research.pdf", Modality.PDF)

ensure_case_study_loaded()


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 4px;">
        <div style="color: #ffffff; font-weight: 700; font-size: 15px; display: flex; align-items: center; gap: 8px;">
            <span style="background: #2563eb; width: 26px; height: 26px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 14px;">✨</span>
            InsightAI Navigation
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-menu-item active">🏠 Home</div>
    <div class="sidebar-menu-item">📤 Upload Data</div>
    <div class="sidebar-menu-item">💬 Chat with AI</div>
    <div class="sidebar-menu-item">📁 My Documents</div>
    <div class="sidebar-menu-item">🗄️ Data Sources</div>
    <div class="sidebar-menu-item">⚙️ Settings</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-bottom-card">
        <div style="color: #ffffff; font-weight: 600; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
            <span>✨</span> Ask anything...
        </div>
        Get insights from your documents, data, images, web and more.
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("⚡ Reload Enterprise Case Study", use_container_width=True):
        st.session_state.store.clear()
        ensure_case_study_loaded()
        st.rerun()


# ==========================================
# TOP GLOBAL NAVBAR
# ==========================================
st.markdown("""
<div class="insight-navbar">
    <div class="brand-section">
        <div class="brand-icon">✨</div>
        <div class="brand-title-wrap">
            <span class="brand-title">InsightAI</span>
            <span class="brand-sub">Multi-Modal Enterprise Intelligence & Research Assistant</span>
        </div>
    </div>
    <div class="navbar-right">
        <div class="user-pill">
            <div class="user-avatar">👤</div>
            <span>Hi, Student</span>
            <span style="font-size: 10px; color: #94a3b8;">▼</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Connected Status Badge
st.markdown("""
<div class="status-bar">
    <span class="connected-tag">
        <span class="connected-dot"></span>
        Connected to your data
    </span>
</div>
""", unsafe_allow_html=True)


# ==========================================
# UPPER SECTION: TWO MAIN CARDS
# ==========================================
col_up_left, col_up_right = st.columns([1.08, 1.15])

# LEFT CARD: "Hello! I'm your Multi-Modal Research Assistant"
with col_up_left:
    st.markdown("""
    <div class="dash-card">
        <div class="assistant-header">
            <span style="color: #2563eb;">✨</span>
            <span>Hello! I'm your Multi-Modal Research Assistant</span>
        </div>
        <div class="assistant-desc">
            Upload your files, ask questions in natural language (text or voice), and get AI-powered insights with citations.
        </div>
        
        <div class="modality-grid">
            <div class="mod-card">
                <div class="mod-icon-wrap" style="background: #fee2e2; color: #ef4444;">📄</div>
                <div class="mod-title">PDFs</div>
                <div class="mod-desc">Reports, research papers, policies, manuals</div>
            </div>
            <div class="mod-card">
                <div class="mod-icon-wrap" style="background: #d1fae5; color: #10b981;">📊</div>
                <div class="mod-title">Excel / CSV</div>
                <div class="mod-desc">Sales, finance, employee, customer data</div>
            </div>
            <div class="mod-card">
                <div class="mod-icon-wrap" style="background: #dbeafe; color: #3b82f6;">🖼️</div>
                <div class="mod-title">Images</div>
                <div class="mod-desc">Charts, diagrams, scanned documents</div>
            </div>
            <div class="mod-card">
                <div class="mod-icon-wrap" style="background: #e0f2fe; color: #0284c7;">🌐</div>
                <div class="mod-title">Web Pages</div>
                <div class="mod-desc">Company / research information</div>
            </div>
            <div class="mod-card">
                <div class="mod-icon-wrap" style="background: #ede9fe; color: #8b5cf6;">🎤</div>
                <div class="mod-title">Voice Queries</div>
                <div class="mod-desc">Ask questions verbally</div>
            </div>
            <div class="mod-card">
                <div class="mod-icon-wrap" style="background: #e0e7ff; color: #2563eb;">📝</div>
                <div class="mod-title">Text Documents</div>
                <div class="mod-desc">Reports, meeting notes, & more</div>
            </div>
        </div>

        <div class="upload-dropzone">
            <div style="font-size: 26px; color: #3b82f6;">☁️</div>
            <div class="upload-main-text">Drag & drop files here or click to upload</div>
            <div class="upload-sub-text">Supports PDF, Excel, CSV, Images (PNG/JPG), Web links, Text files, Audio (MP3/WAV)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# RIGHT CARD: Chat & AI Analysis
with col_up_right:
    st.markdown("""
    <div class="dash-card">
        <!-- User Query Bubble -->
        <div class="chat-user-msg">
            <div class="chat-user-bubble">
                <div style="display: flex; align-items: flex-start; gap: 8px;">
                    <span style="font-size: 14px;">👤</span>
                    <div>Why did our revenue decrease in Q3, and what are the major market factors responsible?</div>
                </div>
                <div class="chat-time">10:24 AM</div>
            </div>
        </div>

        <!-- AI Assistant Response -->
        <div class="chat-ai-header">
            <div class="ai-avatar">✨</div>
            <span style="font-weight: 600; font-size: 13px; color: #0f172a;">InsightAI Research Analyst</span>
        </div>

        <div class="ai-content">
            Here's a detailed analysis based on the documents and data you provided:<br/><br/>
            <strong>1. Revenue Decrease in Q3</strong><br/>
            The company's revenue decreased by <strong>12.4%</strong> in Q3 2024 compared to Q2 2024, mainly due to lower product sales and a decline in the international market.<br/><br/>
            <strong>2. Key Market Factors</strong><br/>
            • <strong>Increased competition</strong> — New entrants in the market led to price pressure.<br/>
            • <strong>Changing customer preferences</strong> — Shift towards alternative products.<br/>
            • <strong>Economic slowdown</strong> — Reduced spending in key regions (Europe and APAC).<br/>
            • <strong>Supply chain disruptions</strong> — Delays in raw material supply affected production.<br/><br/>
            <em>The analysis is based on the <strong>Annual Report (p. 18-22)</strong>, <strong>Q3 Sales Data (Excel)</strong>, <strong>Market Research Report (p. 6-10)</strong>, and product insights from the image.</em>
        </div>

        <!-- Visual Summary Header -->
        <div style="font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
            <span>📊</span> Visual Summary
        </div>
    """, unsafe_allow_html=True)

    # 3 Mini visual summaries side-by-side inside chat
    c_sum1, c_sum2, c_sum3 = st.columns([1, 1, 0.9])
    with c_sum1:
        st.plotly_chart(EnterpriseChartGenerator.create_mini_q2_q3_chart(), use_container_width=True, config={'displayModeBar': False})
    with c_sum2:
        st.plotly_chart(EnterpriseChartGenerator.create_mini_donut_chart(), use_container_width=True, config={'displayModeBar': False})
    with c_sum3:
        screen_img_path = SAMPLE_DATA_DIR / "Product_Screenshot.png"
        if screen_img_path.exists():
            st.image(str(screen_img_path), caption="Product_Screenshot.png (+2 more)", use_container_width=True)

    # Sources Pills at bottom of Chat Card
    st.markdown("""
        <div class="sources-bar">
            <span style="font-weight: 600;">Sources:</span>
            <span class="source-badge">📄 Annual_Report.pdf (p.18-22)</span>
            <span class="source-badge">📊 Sales_Data.xlsx (Q3 Sheet)</span>
            <span class="source-badge">📄 Market_Research.pdf (p.6-10)</span>
            <a href="#sources" style="color: #2563eb; text-decoration: none; font-weight: 600; margin-left: 6px;">View all sources →</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Interactive Chat Input Bar with Mic Icon
    col_in_mic, col_in_text = st.columns([0.08, 0.92])
    with col_in_mic:
        st.button("🎙️", help="Click to ask question with Voice")
    with col_in_text:
        st.chat_input("Ask a question...")


# ==========================================
# BOTTOM ROW: 4 CLEAN PANELS
# ==========================================
col_b1, col_b2, col_b3, col_b4 = st.columns(4)

# ------------------------------------------
# PANEL 1: Upload Files / Add Sources
# ------------------------------------------
with col_b1:
    st.markdown("""
    <div class="panel-box">
        <div class="panel-header">1. Upload Files / Add Sources</div>
        <div style="font-size: 12.5px; font-weight: 600; color: #1e293b; margin-bottom: 2px;">Upload Files</div>
        <div style="font-size: 11px; color: #64748b; margin-bottom: 10px;">Add multiple file types to build your knowledge base.</div>

        <div style="border: 1.5px dashed #cbd5e1; background: #f8fafc; border-radius: 8px; padding: 14px 10px; text-align: center; margin-bottom: 10px;">
            <div style="font-size: 20px; color: #3b82f6;">☁️</div>
            <div style="font-size: 11.5px; font-weight: 600; color: #334155;">Drag & drop files here or click to upload</div>
        </div>

        <div style="display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 12px;">
            <span style="background: #fee2e2; color: #ef4444; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">PDF</span>
            <span style="background: #d1fae5; color: #10b981; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Excel</span>
            <span style="background: #d1fae5; color: #10b981; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">CSV</span>
            <span style="background: #dbeafe; color: #3b82f6; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Image</span>
            <span style="background: #e0f2fe; color: #0284c7; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Web Link</span>
            <span style="background: #e0e7ff; color: #2563eb; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Text</span>
            <span style="background: #ede9fe; color: #8b5cf6; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Audio</span>
        </div>

        <!-- Ingested Files List -->
        <div class="file-item">
            <div class="file-info">
                <span style="color: #ef4444;">📄</span>
                <div>
                    <div class="file-name">Annual_Report.pdf</div>
                    <div class="file-size">2.4 MB</div>
                </div>
            </div>
            <div class="upload-status">✓ Uploaded <span style="color: #94a3b8; margin-left: 6px; cursor: pointer;">✕</span></div>
        </div>

        <div class="file-item">
            <div class="file-info">
                <span style="color: #10b981;">📊</span>
                <div>
                    <div class="file-name">Sales_Data.xlsx</div>
                    <div class="file-size">1.2 MB</div>
                </div>
            </div>
            <div class="upload-status">✓ Uploaded <span style="color: #94a3b8; margin-left: 6px; cursor: pointer;">✕</span></div>
        </div>

        <div class="file-item">
            <div class="file-info">
                <span style="color: #3b82f6;">🖼️</span>
                <div>
                    <div class="file-name">Product_Screenshot.png</div>
                    <div class="file-size">856 KB</div>
                </div>
            </div>
            <div class="upload-status">✓ Uploaded <span style="color: #94a3b8; margin-left: 6px; cursor: pointer;">✕</span></div>
        </div>

        <div class="file-item">
            <div class="file-info">
                <span style="color: #ef4444;">📄</span>
                <div>
                    <div class="file-name">Market_Research.pdf</div>
                    <div class="file-size">3.1 MB</div>
                </div>
            </div>
            <div class="upload-status">✓ Uploaded <span style="color: #94a3b8; margin-left: 6px; cursor: pointer;">✕</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------
# PANEL 2: Data Preview & Understanding
# ------------------------------------------
with col_b2:
    st.markdown("""
    <div class="panel-box">
        <div class="panel-header">2. Data Preview & Understanding</div>
        
        <!-- Filter Tabs -->
        <div style="display: flex; gap: 8px; font-size: 11px; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px;">
            <span style="color: #64748b; cursor: pointer;">Documents</span>
            <span style="color: #2563eb; font-weight: 700; border-bottom: 2px solid #2563eb; padding-bottom: 4px; cursor: pointer;">Excel/CSV</span>
            <span style="color: #64748b; cursor: pointer;">Images</span>
            <span style="color: #64748b; cursor: pointer;">Web</span>
            <span style="color: #64748b; cursor: pointer;">Text</span>
        </div>

        <div style="font-size: 12px; font-weight: 700; color: #1e293b; margin-bottom: 2px; display: flex; align-items: center; gap: 6px;">
            <span style="color: #10b981;">📊</span> Sales_Data.xlsx
        </div>
        <div style="font-size: 11px; color: #64748b; margin-bottom: 8px;">Preview (Q3 2024)</div>

        <!-- Excel Data Table Preview -->
        <table class="mini-table">
            <thead>
                <tr>
                    <th>Month</th>
                    <th>Revenue (₹)</th>
                    <th>Units Sold</th>
                    <th>Profit (₹)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Jul 2024</td>
                    <td>12,50,000</td>
                    <td>3,200</td>
                    <td>2,10,000</td>
                </tr>
                <tr>
                    <td>Aug 2024</td>
                    <td>11,80,000</td>
                    <td>2,950</td>
                    <td>1,85,000</td>
                </tr>
                <tr>
                    <td>Sep 2024</td>
                    <td>10,20,000</td>
                    <td>2,500</td>
                    <td>1,20,000</td>
                </tr>
            </tbody>
        </table>

        <div style="text-align: left; margin-bottom: 12px;">
            <a href="#" style="color: #2563eb; font-size: 11px; text-decoration: none; font-weight: 600;">View full data →</a>
        </div>

        <!-- Image Understanding section -->
        <div style="font-size: 12px; font-weight: 700; color: #1e293b; margin-bottom: 6px;">Image Understanding</div>
    """, unsafe_allow_html=True)

    c_img_thumb, c_img_info = st.columns([1, 1.4])
    with c_img_thumb:
        screen_img_path = SAMPLE_DATA_DIR / "Product_Screenshot.png"
        if screen_img_path.exists():
            st.image(str(screen_img_path), use_container_width=True)
    with c_img_info:
        st.markdown("""
        <div style="font-size: 11px; color: #0f172a; font-weight: 600; line-height: 1.3;">Chart detected:</div>
        <div style="font-size: 10.5px; color: #64748b; line-height: 1.3;">Product performance across regions (from Product_Screenshot.png)</div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------
# PANEL 3: Generated Visual Insights
# ------------------------------------------
with col_b3:
    st.markdown("""
    <div class="panel-box">
        <div class="panel-header">3. Generated Visual Insights</div>
    """, unsafe_allow_html=True)

    # Plotly Bar Chart: Revenue Comparison (Q2 vs Q3 2024)
    st.plotly_chart(EnterpriseChartGenerator.create_revenue_comparison_bar(), use_container_width=True, config={'displayModeBar': False})

    # Plotly Donut Chart: Market Factors Contribution
    st.plotly_chart(EnterpriseChartGenerator.create_market_factors_donut(), use_container_width=True, config={'displayModeBar': False})

    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------
# PANEL 4: Sources & Citations
# ------------------------------------------
with col_b4:
    st.markdown("""
    <div class="panel-box" id="sources">
        <div class="panel-header">4. Sources & Citations</div>

        <!-- Tabs -->
        <div style="display: flex; gap: 8px; font-size: 11px; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px;">
            <span style="color: #2563eb; font-weight: 700; border-bottom: 2px solid #2563eb; padding-bottom: 4px; cursor: pointer;">All Sources</span>
            <span style="color: #64748b; cursor: pointer;">Documents</span>
            <span style="color: #64748b; cursor: pointer;">Excel</span>
            <span style="color: #64748b; cursor: pointer;">Images</span>
            <span style="color: #64748b; cursor: pointer;">Web</span>
        </div>

        <!-- Citation Item 1 -->
        <div class="cite-item">
            <div class="cite-item-header">
                <span style="color: #ef4444;">📄</span>
                <span>Annual_Report.pdf (p.18-22)</span>
            </div>
            <div class="cite-item-quote">
                "Revenue decreased by 12.4% in Q3 2024 due to lower product sales and international market decline..."
            </div>
        </div>

        <!-- Citation Item 2 -->
        <div class="cite-item">
            <div class="cite-item-header">
                <span style="color: #10b981;">📊</span>
                <span>Sales_Data.xlsx (Q3 Sheet)</span>
            </div>
            <div class="cite-item-quote">
                "Q3 revenue figures show a 12.4% drop compared to Q2..."
            </div>
        </div>

        <!-- Citation Item 3 -->
        <div class="cite-item">
            <div class="cite-item-header">
                <span style="color: #ef4444;">📄</span>
                <span>Market_Research.pdf (p.6-10)</span>
            </div>
            <div class="cite-item-quote">
                "Key factors include increased competition, changing customer preferences and economic slowdown..."
            </div>
        </div>

        <!-- Citation Item 4 -->
        <div class="cite-item">
            <div class="cite-item-header">
                <span style="color: #3b82f6;">🖼️</span>
                <span>Product_Screenshot.png</span>
            </div>
            <div class="cite-item-quote">
                "Product performance across regions shows a decline in international sales..."
            </div>
        </div>

        <div style="text-align: center; margin-top: 10px;">
            <a href="#" style="color: #2563eb; font-size: 11px; text-decoration: none; font-weight: 600;">View all sources →</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
