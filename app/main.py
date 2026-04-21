import os
import uuid
import streamlit as st

from core.config import CHROMA_DIR
from core.config import UPLOAD_DIR
from core.pdf_loader import load_pdf_pages

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="DocGuard AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --bg-base:      #080c10;
    --bg-surface:   #0d1117;
    --bg-elevated:  #131920;
    --bg-card:      #161d26;
    --border:       #1e2d3d;
    --border-glow:  #1a3a5c;
    --accent:       #00d4ff;
    --accent-dim:   #0099bb;
    --accent-glow:  rgba(0, 212, 255, 0.12);
    --success:      #00e5a0;
    --success-dim:  rgba(0, 229, 160, 0.1);
    --warning:      #ffb340;
    --warning-dim:  rgba(255, 179, 64, 0.1);
    --danger:       #ff4d6a;
    --danger-dim:   rgba(255, 77, 106, 0.1);
    --text-primary: #e8edf2;
    --text-secondary: #7a8fa6;
    --text-muted:   #3d5166;
    --font-display: 'Syne', sans-serif;
    --font-mono:    'JetBrains Mono', monospace;
}

html, body, .stApp {
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-display) !important;
}
#MainMenu, footer, header { display: none !important; }
.stDeployButton { display: none !important; }
.main .block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1100px !important; }
[data-testid="stSidebar"] { background: var(--bg-surface) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] > div { padding: 2rem 1.5rem !important; }

.dg-title { font-family: var(--font-display); font-size: 2.2rem; font-weight: 800; color: var(--text-primary); letter-spacing: -0.02em; line-height: 1; margin: 0; }
.dg-title span { color: var(--accent); }
.dg-subtitle { font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-secondary); letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.4rem; }
.dg-divider { height: 1px; background: linear-gradient(90deg, var(--accent) 0%, var(--border) 40%, transparent 100%); margin: 1.5rem 0 2rem; opacity: 0.4; }

.dg-section { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; }
.dg-section-num { font-family: var(--font-mono); font-size: 0.7rem; color: var(--accent); background: var(--accent-glow); border: 1px solid rgba(0,212,255,0.2); border-radius: 4px; padding: 2px 8px; letter-spacing: 0.05em; }
.dg-section-title { font-family: var(--font-display); font-size: 1rem; font-weight: 600; color: var(--text-primary); letter-spacing: -0.01em; }

.dg-metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; margin-bottom: 1.5rem; }
.dg-metric { background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1rem 1.25rem; text-align: center; }
.dg-metric-val { font-family: var(--font-mono); font-size: 1.6rem; font-weight: 500; color: var(--accent); line-height: 1; margin-bottom: 0.3rem; }
.dg-metric-label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em; }

.dg-badge { display: inline-flex; align-items: center; gap: 0.4rem; font-family: var(--font-mono); font-size: 0.72rem; padding: 4px 10px; border-radius: 20px; letter-spacing: 0.04em; }
.dg-badge-ok   { background: var(--success-dim); border: 1px solid rgba(0,229,160,0.3); color: var(--success); }
.dg-badge-warn { background: var(--warning-dim); border: 1px solid rgba(255,179,64,0.3); color: var(--warning); }

.dg-evidence { background: var(--bg-elevated); border: 1px solid var(--border); border-left: 3px solid var(--accent-dim); border-radius: 0 8px 8px 0; padding: 0.875rem 1rem; margin-bottom: 0.5rem; font-family: var(--font-mono); font-size: 0.75rem; }
.dg-evidence-meta { color: var(--accent); font-size: 0.68rem; margin-bottom: 0.4rem; letter-spacing: 0.04em; }
.dg-evidence-text { color: var(--text-secondary); line-height: 1.6; }
.dg-answer { background: var(--bg-elevated); border: 1px solid var(--border-glow); border-radius: 10px; padding: 1.25rem 1.5rem; font-size: 0.9rem; line-height: 1.75; color: var(--text-primary); margin-bottom: 1.5rem; box-shadow: 0 0 30px rgba(0,212,255,0.04); }

/* ── Summary teaser ── */
.dg-summary-teaser {
    background: var(--bg-card);
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 12px;
    padding: 1.1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-family: var(--font-mono);
    font-size: 0.82rem;
    color: var(--accent);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    box-shadow: 0 0 18px rgba(0,212,255,0.06);
    margin-bottom: 0.75rem;
}
.dg-summary-teaser-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
    animation: pulse-dot 1.8s ease-in-out infinite;
    flex-shrink: 0;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(1.4); }
}

/* ── Summary revealed ── */
.dg-summary-revealed {
    animation: fade-slide-in 0.5s ease forwards;
    background: var(--bg-elevated);
    border: 1px solid var(--border-glow);
    border-left: 3px solid var(--accent);
    border-radius: 0 12px 12px 0;
    padding: 1.25rem 1.5rem;
    font-size: 0.88rem;
    line-height: 1.8;
    color: var(--text-primary);
    margin-bottom: 0.75rem;
}
@keyframes fade-slide-in {
    from { opacity: 0; transform: translateY(-10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.dg-summary-label {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    color: var(--accent);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.dg-summary-label::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0,212,255,0.3), transparent); }

.stButton > button { background: transparent !important; border: 1px solid var(--accent) !important; color: var(--accent) !important; font-family: var(--font-mono) !important; font-size: 0.8rem !important; letter-spacing: 0.06em !important; padding: 0.5rem 1.5rem !important; border-radius: 6px !important; transition: all 0.2s !important; }
.stButton > button:hover { background: var(--accent-glow) !important; box-shadow: 0 0 15px var(--accent-glow) !important; }
.stTextInput > div > div > input { background: var(--bg-elevated) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; color: var(--text-primary) !important; font-family: var(--font-display) !important; font-size: 0.9rem !important; padding: 0.625rem 1rem !important; }
.stTextInput > div > div > input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px var(--accent-glow) !important; }
.stTextInput > div > div > input::placeholder { color: var(--text-muted) !important; }
.stFileUploader { background: var(--bg-card) !important; border: 1px dashed var(--border) !important; border-radius: 10px !important; padding: 0.5rem !important; }
.stSpinner > div { border-color: var(--accent) transparent transparent transparent !important; }
.stAlert { border-radius: 8px !important; border: none !important; font-family: var(--font-mono) !important; font-size: 0.8rem !important; }
.stSuccess { background: var(--success-dim) !important; color: var(--success) !important; }
.stError   { background: var(--danger-dim) !important; color: var(--danger) !important; }

.dg-chunk { background: var(--bg-elevated); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; }
.dg-chunk-id { font-family: var(--font-mono); font-size: 0.65rem; color: var(--accent-dim); margin-bottom: 0.35rem; letter-spacing: 0.04em; }
.dg-chunk-text { font-size: 0.78rem; color: var(--text-secondary); line-height: 1.55; }
.dg-page-preview { background: var(--bg-elevated); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; }
.dg-page-num { font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-muted); margin-bottom: 0.3rem; letter-spacing: 0.06em; text-transform: uppercase; }
.dg-page-text { font-size: 0.78rem; color: var(--text-secondary); line-height: 1.55; }
.dg-sidebar-logo { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--border); }
.dg-sidebar-title { font-family: var(--font-display); font-size: 1rem; font-weight: 700; color: var(--text-primary); }
.dg-sidebar-sub { font-family: var(--font-mono); font-size: 0.6rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; }
.dg-status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--success); display: inline-block; margin-right: 6px; box-shadow: 0 0 6px var(--success); }
.dg-sidebar-info { font-family: var(--font-mono); font-size: 0.68rem; color: var(--text-muted); line-height: 2; margin-bottom: 2rem; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────
for key, default in {
    "pdf_summary":     None,
    "last_pdf_name":   None,
    "summary_visible": False,
    "indexed":         False,
    "page_count":      0,
    "chunk_count":     0,
    "char_count":      0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Imports ───────────────────────────────────────────────────────
from core.chunking     import chunk_pages
from core.embeddings   import embed_texts, embed_query
from core.vector_store import upsert_chunks, query_topk
from core.llm_ollama   import ollama_generate
from core.rag          import answer_question

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="dg-sidebar-logo">
        <div>
            <div class="dg-sidebar-title">DocGuard AI</div>
            <div class="dg-sidebar-sub">v1.0 · Local</div>
        </div>
    </div>
    <div class="dg-sidebar-info">
        <span class="dg-status-dot"></span>Ollama · llama3.1:8b<br>
        <span style="margin-left:12px;color:#3d5166">●</span>&nbsp;ChromaDB · local<br>
        <span style="margin-left:12px;color:#3d5166">●</span>&nbsp;MiniLM-L6-v2<br>
        <span style="margin-left:12px;color:#3d5166">●</span>&nbsp;No cloud · privacy-safe
    </div>
    """, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────
st.markdown("""
<div class="dg-title">Doc<span>Guard</span> AI</div>
<div class="dg-subtitle">Evidence-grounded PDF Q&A · Hallucination prevention · Local-first</div>
<div class="dg-divider"></div>
""", unsafe_allow_html=True)

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

SUMMARY_KEYWORDS = [
    "summarize","summary","overview","abstract","introduction",
    "what is this","what is the document","describe","tell me about",
    "explain this","what does this document","give me a summary",
    "brief","outline","main topic","key points","purpose","objective",
    "what is it about","about this","document about","paper about",
    "report about","what does it cover","author aim","what does author",
    "what is the aim","goal of","objective of"
]

# ── Section 01: Upload ────────────────────────────────────────────
st.markdown("""
<div class="dg-section">
    <span class="dg-section-num">01</span>
    <span class="dg-section-title">Upload Document</span>
</div>
""", unsafe_allow_html=True)

pdf = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

if pdf is not None:
    st.markdown(f"""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
                color:#7a8fa6;margin:0.5rem 0 1rem;letter-spacing:0.04em;">
        ◆ &nbsp;{pdf.name}
    </div>
    """, unsafe_allow_html=True)

    # ── Clear old index when a new PDF is uploaded ────────────────
    if st.session_state["last_pdf_name"] != pdf.name:
        try:
            import chromadb
            from chromadb.config import Settings as CSettings
            _c = chromadb.PersistentClient(
                path=CHROMA_DIR,
                settings=CSettings(anonymized_telemetry=False)
            )
            _c.delete_collection("citecheck")
        except Exception:
            pass
        st.session_state["last_pdf_name"]   = pdf.name
        st.session_state["pdf_summary"]     = None
        st.session_state["summary_visible"] = False
        st.session_state["indexed"]         = False
        st.session_state["page_count"]      = 0
        st.session_state["chunk_count"]     = 0
        st.session_state["char_count"]      = 0

    # ── Index only once per PDF ───────────────────────────────────
    if not st.session_state["indexed"]:
        file_id   = str(uuid.uuid4())[:8]
        save_path = os.path.join(UPLOAD_DIR, f"{file_id}_{pdf.name}")
        with open(save_path, "wb") as f:
            f.write(pdf.getbuffer())

        st.success(f"Saved · {save_path}")
        pages = load_pdf_pages(save_path)

        if not pages:
            st.error("No extractable text found. This may be a scanned PDF.")
        else:
            chunks = chunk_pages(pages)

            st.session_state["page_count"]  = len(pages)
            st.session_state["chunk_count"] = len(chunks)
            st.session_state["char_count"]  = sum(len(c.text) for c in chunks)

            with st.expander("Preview chunks", expanded=False):
                for c in chunks[:3]:
                    st.markdown(f"""
                    <div class="dg-chunk">
                        <div class="dg-chunk-id">CHUNK {c.chunk_id} · PAGE {c.page}</div>
                        <div class="dg-chunk-text">{c.text[:280]}{'…' if len(c.text)>280 else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with st.spinner("Embedding and indexing…"):
                embeddings = embed_texts([c.text for c in chunks])
                upsert_chunks(chunks, embeddings, doc_name=pdf.name)

            st.success("Indexed in ChromaDB · Ready for queries")
            st.session_state["indexed"] = True

            # ── Generate summary — bypass guard, call LLM directly ─
            with st.spinner("Generating summary…"):
                try:
                    q_emb = embed_query(
                        "summary overview introduction what is this document about main topic"
                    )
                    res       = query_topk(q_emb, k=8)
                    top_docs  = res["documents"][0]
                    top_metas = res["metadatas"][0]

                    context = "\n\n".join(
                        f"[Page {top_metas[i]['page']}] {top_docs[i][:400]}"
                        for i in range(len(top_docs))
                    )

                    prompt = f"""You are DocGuard AI. Using ONLY the document excerpts below,
write a clear and informative summary in 6 sentences.
Cover the main topic, key findings, and purpose of the document.
Do NOT use outside knowledge.

DOCUMENT EXCERPTS:
{context}

SUMMARY:"""

                    summary = ollama_generate(prompt)
                    st.session_state["pdf_summary"] = summary

                except Exception as ex:
                    st.session_state["pdf_summary"] = f"Summary unavailable: {ex}"

            with st.expander("Page preview", expanded=False):
                for p in pages[:2]:
                    st.markdown(f"""
                    <div class="dg-page-preview">
                        <div class="dg-page-num">Page {p.page}</div>
                        <div class="dg-page-text">{p.text[:380]}{'…' if len(p.text)>380 else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)

# ── Sections 02 & 03 — shown once indexed ────────────────────────
if st.session_state["indexed"]:

    # Metrics row
    st.markdown(f"""
    <div class="dg-metrics">
        <div class="dg-metric">
            <div class="dg-metric-val">{st.session_state['page_count']}</div>
            <div class="dg-metric-label">Pages extracted</div>
        </div>
        <div class="dg-metric">
            <div class="dg-metric-val">{st.session_state['chunk_count']}</div>
            <div class="dg-metric-label">Chunks created</div>
        </div>
        <div class="dg-metric">
            <div class="dg-metric-val">{st.session_state['char_count']:,}</div>
            <div class="dg-metric-label">Characters indexed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Section 02: Document Summary ─────────────────────────────
    st.markdown("""<div class="dg-divider"></div>""", unsafe_allow_html=True)
    st.markdown("""
    <div class="dg-section">
        <span class="dg-section-num">02</span>
        <span class="dg-section-title">Document Summary</span>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state["summary_visible"]:
        # Teaser — pulsing dot + reveal button
        st.markdown("""
        <div class="dg-summary-teaser">
            <div class="dg-summary-teaser-dot"></div>
            <span>Summary ready — click to reveal</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("◈  View Document Summary", key="show_summary"):
            st.session_state["summary_visible"] = True
            st.rerun()
    else:
        # Revealed — fade-in summary card
        st.markdown(f"""
        <div class="dg-summary-revealed">
            <div class="dg-summary-label">◆ &nbsp;AI-Generated Summary</div>
            {st.session_state["pdf_summary"]}
        </div>
        """, unsafe_allow_html=True)
        if st.button("↑  Collapse Summary", key="hide_summary"):
            st.session_state["summary_visible"] = False
            st.rerun()

    # ── Section 03: Ask a Question ────────────────────────────────
    st.markdown("""<div class="dg-divider"></div>""", unsafe_allow_html=True)
    st.markdown("""
    <div class="dg-section">
        <span class="dg-section-num">03</span>
        <span class="dg-section-title">Ask a Question</span>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_input(
        "",
        placeholder="What does this document say about…",
        label_visibility="collapsed"
    )

    col_btn, col_space = st.columns([1, 5])
    with col_btn:
        ask = st.button("ASK →")

    if ask and question.strip():
        q_lower      = question.lower()
        is_summary_q = any(kw in q_lower for kw in SUMMARY_KEYWORDS)

        if is_summary_q and st.session_state["pdf_summary"]:
            # Return cached summary — no LLM call needed
            st.markdown(
                '<div style="margin-bottom:1rem;">'
                '<span class="dg-badge dg-badge-ok">● GUARD PASSED</span>'
                '</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div class="dg-section">'
                '<span class="dg-section-num">ANS</span>'
                '<span class="dg-section-title">Answer</span>'
                '</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="dg-answer">{st.session_state["pdf_summary"]}</div>',
                unsafe_allow_html=True
            )

        else:
            # Full RAG pipeline
            with st.spinner("Retrieving evidence and reasoning…"):
                answer, evidence, guard_status = answer_question(question)

            badge = (
                '<span class="dg-badge dg-badge-ok">● GUARD PASSED</span>'
                if guard_status == "OK" else
                '<span class="dg-badge dg-badge-warn">⚠ GUARD REFUSED</span>'
            )
            st.markdown(
                f'<div style="margin-bottom:1rem;">{badge}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div class="dg-section">'
                '<span class="dg-section-num">ANS</span>'
                '<span class="dg-section-title">Answer</span>'
                '</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="dg-answer">{answer}</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="dg-section">'
                '<span class="dg-section-num">SRC</span>'
                '<span class="dg-section-title">Source Evidence</span>'
                '</div>',
                unsafe_allow_html=True
            )
            for i, e in enumerate(evidence[:5], 1):
                doc     = e.__dict__.get("doc", pdf.name if pdf else "document")
                snippet = e.text[:240] + ("…" if len(e.text) > 240 else "")
                st.markdown(f"""
                <div class="dg-evidence">
                    <div class="dg-evidence-meta">
                        [{i}] &nbsp;{doc} &nbsp;·&nbsp; Page {e.page} &nbsp;·&nbsp; dist={e.distance:.3f}
                    </div>
                    <div class="dg-evidence-text">{snippet}</div>
                </div>
                """, unsafe_allow_html=True)

            if guard_status != "OK":
                st.markdown(f"""
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
                            color:#ffb340;margin-top:1rem;padding:0.75rem 1rem;
                            background:rgba(255,179,64,0.06);
                            border:1px solid rgba(255,179,64,0.2);border-radius:8px;">
                    ⚠ &nbsp;{guard_status}
                </div>
                """, unsafe_allow_html=True)