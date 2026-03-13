import logging
import sys
from pathlib import Path
import os
import csv
import datetime as dt
import json

# project path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from config.config import KNOWLEDGE_DIR, PROJECT_ROOT
from models.llm import get_chat_completion
from utils.rag_utils import (
    load_and_index_knowledge_base,
    retrieve,
    chunk_text,
    build_index,
)
from utils.web_search import live_web_search
from utils.youtube_search import search_youtube

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Page config

st.set_page_config(
    page_title="NeoInvest Insight",
    page_icon="📈",
    layout="centered"
)

#  UI 

st.markdown(
    """
    <style>
    /* 1. MAIN APP BACKGROUND */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"] {
        background-color: #0B3D2E !important;
        color: #F5F5F0;
    }
    
    /* 2. SIDEBAR FORMATTING */
    [data-testid="stSidebar"] {
        background-color: #0B3D2E !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding-top: 2rem;
    }

    /* 3. HEADER CARD */
    .header-card {
        background: linear-gradient(135deg, #14532D, #0B3D2E);
        border-radius: 20px;
        padding: 50px 20px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        margin-bottom: 30px;
    }
    .header-card h1 { font-size: 3rem !important; margin: 0 !important; color: white !important; font-weight: 800 !important; }
    .header-card p { font-size: 1.1rem !important; color: #A0C49D !important; margin-top: 10px !important; }

    /* 4. FILE UPLOADER */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px;
        padding: 20px;
    }

    /* 5. QUICK ACTION BUTTONS (Your Hover Style) */
    div.stButton > button {
        background-color: #14532D !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 12px 15px !important;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #1B5E20 !important;
        border-color: #4ade80 !important;
        transform: translateY(-2px);
    }

    /* 6. CHAT MESSAGES */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        margin-bottom: 15px !important;
    }

    /* 7. INPUT FIELD STYLE */
    .stTextInput input {
        background-color: #14532D !important;
        color: #F5F5F0 !important;
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    p, span, label, h1, h2, h3 { color: #F5F5F0 !important; font-family: 'Inter', sans-serif; }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# Session State
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "saved_sessions" not in st.session_state:
    st.session_state.saved_sessions = []

# --------------------------------------------------
# Logic Functions
# --------------------------------------------------
@st.cache_resource
def get_rag_index():
    try:
        chunks, vectors = load_and_index_knowledge_base()
        return chunks, vectors
    except Exception as e:
        logger.exception("RAG index build failed: %s", e)
        return [], []

def get_rag_context(query: str):
    chunks, vectors = get_rag_index()
    uploaded_chunks = st.session_state.get("uploaded_chunks")
    uploaded_vectors = st.session_state.get("uploaded_vectors")
    if uploaded_chunks and uploaded_vectors:
        chunks = list(chunks) + list(uploaded_chunks)
        vectors = list(vectors) + list(uploaded_vectors)
    if not chunks or not vectors: return ""
    retrieved = retrieve(query, chunks, vectors)
    if not retrieved: return ""
    return "Relevant knowledge base excerpts:\n" + "\n\n---\n\n".join(retrieved)

def build_system_prompt(rag_context, web_context, youtube_context, response_mode, risk_profile, market_focus):
    base = "You are an AI Investment Research Assistant. "
    if response_mode == "Concise": base += "Respond in 2-3 sentences.\n"
    else: base += "Provide a detailed explanation with bullet points.\n"
    parts = [base]
    if rag_context: parts.append("\n\n--- Knowledge Base ---\n" + rag_context)
    if web_context: parts.append("\n\n--- Live Web Search ---\n" + web_context)
    if youtube_context: parts.append("\n\n--- YouTube Insights ---\n" + youtube_context)
    return "\n".join(parts)

# --------------------------------------------------
# Main App Structure
# --------------------------------------------------
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("**Settings**")
        response_mode = st.radio("Mode", ["Concise", "Detailed"], index=1)
        risk_profile = st.radio("Risk", ["Conservative", "Balanced", "Aggressive"], index=1)
        market_focus = st.radio("Market", ["Both", "India", "US"], index=0)
        st.divider()

        # Session controls
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

        # Load saved sessions from disk once
        sessions_path = Path("logs") / "sessions.json"
        if not st.session_state.saved_sessions and sessions_path.exists():
            try:
                data = json.load(sessions_path.open())
                if isinstance(data, list):
                    st.session_state.saved_sessions = data
            except Exception as e:
                logger.warning("Could not load saved sessions: %s", e)

        st.markdown("---")
        st.markdown("**Saved sessions**")
        options = ["Current session"] + [s.get("name", f"Session {i+1}") for i, s in enumerate(st.session_state.saved_sessions)]
        selected = st.selectbox("View session", options, index=0)

        col_save, col_load = st.columns(2)
        with col_save:
            if st.button("Save current", use_container_width=True):
                os.makedirs("logs", exist_ok=True)
                new_id = len(st.session_state.saved_sessions) + 1
                session = {
                    "id": new_id,
                    "name": f"Session {new_id}",
                    "messages": st.session_state.messages,
                }
                st.session_state.saved_sessions.append(session)
                try:
                    with (Path("logs") / "sessions.json").open("w") as f:
                        json.dump(st.session_state.saved_sessions, f, indent=2)
                    st.success(f"Saved as Session {new_id}")
                except Exception as e:
                    logger.warning("Could not save sessions: %s", e)
        with col_load:
            if st.button("Load selected", use_container_width=True) and selected != "Current session":
                idx = options.index(selected) - 1
                if 0 <= idx < len(st.session_state.saved_sessions):
                    st.session_state.messages = st.session_state.saved_sessions[idx].get("messages", [])
                    st.rerun()

    # Header Card
    st.markdown(
        '<div class="header-card"><h1>📈 NeoInvest Insight</h1><p>Investment Research Assistant for Indian & US Markets</p></div>',
        unsafe_allow_html=True,
    )

    # File Uploader (TXT / MD / PDF / DOCX)
    uploaded_file = st.file_uploader(
        "Upload research notes (TXT / MD / PDF / DOCX)",
        type=["txt", "md", "pdf", "docx"],
    )

    uploaded_text = None
    if uploaded_file is not None:
        suffix = (uploaded_file.name or "").lower().rsplit(".", 1)[-1]

        if suffix in ("txt", "md"):
            uploaded_text = uploaded_file.read().decode("utf-8", errors="replace")
        elif suffix == "pdf":
            try:
                from pypdf import PdfReader

                reader = PdfReader(uploaded_file)
                pages = []
                for page in reader.pages:
                    try:
                        pages.append(page.extract_text() or "")
                    except Exception:
                        continue
                uploaded_text = "\n\n".join(pages).strip()
            except Exception as e:
                logger.warning("PDF extraction failed: %s", e)
        elif suffix == "docx":
            try:
                from docx import Document

                doc = Document(uploaded_file)
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                uploaded_text = "\n".join(paragraphs).strip()
            except Exception as e:
                logger.warning("DOCX extraction failed: %s", e)

        if uploaded_text:
            chunks = [("uploaded_notes", c) for c in chunk_text(uploaded_text)]
            uploaded_chunks, uploaded_vectors = build_index(chunks)
            st.session_state.uploaded_chunks = uploaded_chunks
            st.session_state.uploaded_vectors = uploaded_vectors
            st.success("Uploaded research added to this session's context.")
        else:
            st.warning("Could not extract text from this file.")

    # --------------------------------------------------
    # INPUT AREA (Top placement keeps color uniform)
    # --------------------------------------------------
    st.markdown("Ask about stocks or markets...")
    user_query = st.text_input("", placeholder="e.g. Reliance", key="query_input", label_visibility="collapsed")

    # Quick Actions
    st.markdown("### Quick actions")
    col1, col2, col3 = st.columns(3)
    
    button_query = None
    with col1:
        if st.button("Compare two stocks"):
            if user_query: button_query = f"Compare {user_query} for long-term investing."
            else: st.warning("Please enter a stock name first!")
    with col2:
        if st.button("Explain a stock"):
            if user_query: button_query = f"Explain {user_query} stock to a beginner."
            else: st.warning("Please enter a stock name first!")
    with col3:
        if st.button("Latest stock news"):
            if user_query: button_query = f"Summarise the latest news about {user_query} stock."
            else: st.warning("Please enter a stock name first!")

    st.divider()

    # LOGIC
    # Check if user typed and hit Enter OR clicked a button
    final_query = None
    if user_query and (st.session_state.get('last_trigger') != user_query):
        final_query = user_query
        st.session_state['last_trigger'] = user_query
    elif button_query:
        final_query = button_query

    if final_query:
        st.session_state.messages.append({"role": "user", "content": final_query})
        
        with st.status("Analyzing market data...") as status:
            try:
                rag_context = get_rag_context(final_query)
                web_context = live_web_search(final_query)
                youtube_context = search_youtube(final_query)
                system_p = build_system_prompt(rag_context, web_context, youtube_context, response_mode, risk_profile, market_focus)
                
                messages = [{"role": "system", "content": system_p}]
                for m in st.session_state.messages: messages.append({"role": m["role"], "content": m["content"]})
                
                response = get_chat_completion(messages, temperature=0.5, max_tokens=1400 if response_mode == "Detailed" else 320)
                st.session_state.messages.append({"role": "assistant", "content": response})
                status.update(label="Analysis complete!", state="complete")
            except Exception as e:
                st.error(f"Error: {e}")
        st.rerun()

    # --------------------------------------------------
    # DISPLAY HISTORY (Standard Chat Order: Question -> Answer)
    # --------------------------------------------------
    messages_list = st.session_state.messages
    total = len(messages_list)

    for idx, msg in enumerate(messages_list):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Simple feedback for the latest assistant answer
            if idx == total - 1 and msg["role"] == "assistant":
                feedback = st.radio(
                    "Was this answer helpful?",
                    ["👍 Yes", "👎 No"],
                    horizontal=True,
                    key=f"fb_{total}",
                )
                try:
                    os.makedirs("logs", exist_ok=True)
                    with open("logs/feedback.csv", "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            [
                                dt.datetime.utcnow().isoformat(),
                                # latest user message just before this assistant
                                messages_list[-2]["content"]
                                if total >= 2
                                else "",
                                "yes" if feedback == "👍 Yes" else "no",
                            ]
                        )
                except Exception as log_err:
                    logger.warning("Could not write feedback log: %s", log_err)

if __name__ == "__main__":
    main()
