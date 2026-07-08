from __future__ import annotations

import shutil
import uuid
from dataclasses import replace
from pathlib import Path
import sys

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from rag_mvp.config import load_settings
from rag_mvp.ingestion import ingest_documents
from rag_mvp.retrieval import answer_question


load_dotenv()
st.set_page_config(page_title="RAG Upload + Ask", page_icon="📄", layout="centered")

st.title("📄 RAG Upload + Ask")
st.caption("Upload documents, build an index, and ask grounded questions.")

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:10]
if "index_ready" not in st.session_state:
    st.session_state.index_ready = False
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []

base_settings = load_settings()
session_id = st.session_state.session_id

data_dir = Path("uploaded_data") / session_id
db_dir = Path("uploaded_chroma") / session_id
settings = replace(base_settings, data_dir=data_dir, db_dir=db_dir)

if not settings.google_api_key:
    st.warning("Missing GOOGLE_API_KEY. Add it to `.env` before asking questions.")

uploaded_files = st.file_uploader(
    "Upload files (.pdf, .txt, .md)",
    type=["pdf", "txt", "md"],
    accept_multiple_files=True,
)

col1, col2 = st.columns(2)
with col1:
    build_clicked = st.button("Build index", use_container_width=True)
with col2:
    reset_clicked = st.button("Reset session", use_container_width=True)

if reset_clicked:
    if data_dir.exists():
        shutil.rmtree(data_dir)
    if db_dir.exists():
        shutil.rmtree(db_dir)
    st.session_state.index_ready = False
    st.session_state.indexed_files = []
    st.success("Session reset. Upload files and build index again.")

if build_clicked:
    try:
        if not uploaded_files:
            st.error("Upload at least one file before building the index.")
        else:
            if data_dir.exists():
                shutil.rmtree(data_dir)
            data_dir.mkdir(parents=True, exist_ok=True)

            saved_names: list[str] = []
            for uploaded in uploaded_files:
                destination = data_dir / uploaded.name
                destination.write_bytes(uploaded.getbuffer())
                saved_names.append(uploaded.name)

            with st.spinner("Indexing uploaded files..."):
                doc_count, chunk_count = ingest_documents(settings, force_rebuild=True)

            st.session_state.index_ready = True
            st.session_state.indexed_files = saved_names
            st.success(
                f"Index ready: {doc_count} document(s), {chunk_count} chunk(s) indexed."
            )
    except Exception as exc:
        st.session_state.index_ready = False
        st.error(f"Failed to build index: {exc}")

if st.session_state.indexed_files:
    st.subheader("Indexed files")
    for name in st.session_state.indexed_files:
        st.write(f"- {name}")

st.divider()
question = st.text_input("Ask a question from your uploaded files")
ask_clicked = st.button("Get answer", type="primary", use_container_width=True)

if ask_clicked:
    try:
        if not st.session_state.index_ready:
            st.error("Build the index first.")
        elif not question.strip():
            st.error("Enter a question.")
        else:
            with st.spinner("Retrieving answer..."):
                answer, docs = answer_question(settings, question.strip())

            st.subheader("Answer")
            st.write(answer)

            st.subheader("Sources")
            if not docs:
                st.write("No matching chunks found.")
            else:
                seen: set[str] = set()
                for doc in docs:
                    source = str(doc.metadata.get("source", "unknown"))
                    source_name = Path(source).name
                    if source_name in seen:
                        continue
                    seen.add(source_name)
                    st.write(f"- {source_name}")
    except Exception as exc:
        st.error(f"Failed to answer: {exc}")
