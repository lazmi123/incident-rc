from __future__ import annotations

import re
import shutil
from dataclasses import replace
from pathlib import Path
import sys

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from rag_mvp.config import load_settings
from rag_mvp.ingestion import ingest_documents
from rag_mvp.retrieval import answer_question


def slugify_name(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", name.strip().lower()).strip("-")
    return slug


def list_saved_files(folder: Path) -> list[str]:
    if not folder.exists():
        return []

    files = []
    for path in folder.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".pdf", ".txt", ".md"}:
            files.append(path.name)
    return sorted(files)


load_dotenv()
st.set_page_config(page_title="RAG Upload + Ask", page_icon="📄", layout="centered")

st.title("📄 RAG Upload + Ask")
st.caption("Upload files once, save in ChromaDB, and ask from those sources.")

base_settings = load_settings()
kb_name = st.text_input(
    "Knowledge base name",
    value=st.session_state.get("kb_name", "default"),
    help="Files and vectors are persisted by this name.",
)
st.session_state.kb_name = kb_name

kb_slug = slugify_name(kb_name)
if not kb_slug:
    st.error("Enter a valid knowledge base name (letters/numbers).")
    st.stop()

data_dir = Path("uploaded_data") / kb_slug
db_dir = Path("uploaded_chroma") / kb_slug
settings = replace(base_settings, data_dir=data_dir, db_dir=db_dir)

saved_files = list_saved_files(data_dir)
index_exists = db_dir.exists() and any(db_dir.iterdir())

if not settings.google_api_key:
    st.warning("Missing GOOGLE_API_KEY. Add it to `.env` before asking questions.")

st.info(
    f"Persistent storage:\n- Files: `{data_dir}`\n- ChromaDB: `{db_dir}`",
    icon="💾",
)

if index_exists:
    st.success(
        "Existing Chroma index found for this knowledge base. You can ask now.",
        icon="✅",
    )

uploaded_files = st.file_uploader(
    "Upload files (.pdf, .txt, .md)",
    type=["pdf", "txt", "md"],
    accept_multiple_files=True,
)

col1, col2 = st.columns(2)
with col1:
    build_clicked = st.button("Save files + Build index", use_container_width=True)
with col2:
    reset_clicked = st.button("Delete knowledge base", use_container_width=True)

if reset_clicked:
    if data_dir.exists():
        shutil.rmtree(data_dir)
    if db_dir.exists():
        shutil.rmtree(db_dir)
    st.success(f"Deleted knowledge base '{kb_slug}'.")

if build_clicked:
    try:
        if not uploaded_files and not saved_files:
            st.error("Upload at least one file before building the index.")
        else:
            data_dir.mkdir(parents=True, exist_ok=True)

            uploaded_count = 0
            for uploaded in uploaded_files or []:
                destination = data_dir / uploaded.name
                destination.write_bytes(uploaded.getbuffer())
                uploaded_count += 1

            with st.spinner("Indexing files into ChromaDB..."):
                doc_count, chunk_count = ingest_documents(settings, force_rebuild=True)

            st.success(
                "Index built and persisted.\n"
                f"Uploaded {uploaded_count} file(s) this run.\n"
                f"Indexed {doc_count} document(s) into {chunk_count} chunk(s)."
            )
    except Exception as exc:
        st.error(f"Failed to build index: {exc}")

saved_files = list_saved_files(data_dir)
if saved_files:
    st.subheader("Saved files in this knowledge base")
    for name in saved_files:
        st.write(f"- {name}")

st.divider()
question = st.text_input("Ask a question from the saved source files")
ask_clicked = st.button("Get answer", type="primary", use_container_width=True)

if ask_clicked:
    try:
        if not (db_dir.exists() and any(db_dir.iterdir())):
            st.error("No Chroma index found for this knowledge base. Build index first.")
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
