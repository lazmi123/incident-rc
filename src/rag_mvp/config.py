from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer.") from exc


@dataclass(frozen=True)
class Settings:
    google_api_key: str | None
    gemini_model: str
    embedding_model: str
    data_dir: Path
    db_dir: Path
    top_k: int
    chunk_size: int
    chunk_overlap: int


def load_settings() -> Settings:
    return Settings(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        embedding_model=os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        ),
        data_dir=Path(os.getenv("RAG_DATA_DIR", "data")),
        db_dir=Path(os.getenv("RAG_DB_DIR", "chroma_db")),
        top_k=_int_env("RAG_TOP_K", 4),
        chunk_size=_int_env("RAG_CHUNK_SIZE", 800),
        chunk_overlap=_int_env("RAG_CHUNK_OVERLAP", 120),
    )
