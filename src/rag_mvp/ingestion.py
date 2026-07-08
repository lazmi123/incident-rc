from __future__ import annotations

import shutil
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_mvp.config import Settings
from rag_mvp.embeddings import build_embeddings


def _text_loader(path: str) -> TextLoader:
    return TextLoader(path, encoding="utf-8")


def load_documents(data_dir: Path) -> list[Document]:
    docs: list[Document] = []
    loaders = (
        DirectoryLoader(
            str(data_dir),
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            silent_errors=True,
        ),
        DirectoryLoader(
            str(data_dir),
            glob="**/*.txt",
            loader_cls=_text_loader,
            show_progress=True,
            silent_errors=True,
        ),
        DirectoryLoader(
            str(data_dir),
            glob="**/*.md",
            loader_cls=_text_loader,
            show_progress=True,
            silent_errors=True,
        ),
    )
    for loader in loaders:
        docs.extend(loader.load())
    return docs


def ingest_documents(settings: Settings, force_rebuild: bool = False) -> tuple[int, int]:
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    documents = load_documents(settings.data_dir)
    if not documents:
        raise ValueError(
            f"No documents found in {settings.data_dir}. Add PDF/TXT/MD files and retry."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(documents)

    if force_rebuild and settings.db_dir.exists():
        shutil.rmtree(settings.db_dir)

    settings.db_dir.mkdir(parents=True, exist_ok=True)
    embeddings = build_embeddings(settings)
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(settings.db_dir),
    )
    return len(documents), len(chunks)
