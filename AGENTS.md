# AGENTS.md

## Cursor Cloud specific instructions

This repo is a single Python 3 application: a **LangChain + ChromaDB + Gemini RAG MVP**
(document ingestion → local sentence-transformers embeddings → ChromaDB vector store →
Gemini grounded answers). There is no server/web UI; it is a CLI. See `README.md` for the
full command reference.

### Environment / running caveats
- Dependencies are installed into the system site with `pip install --break-system-packages`.
  `python3 -m venv` does **not** work on this base image (missing `ensurepip`), so a venv is
  intentionally not used; the startup update script installs deps directly.
- `GOOGLE_API_KEY` is provided as a secret/env var, so `.env` is optional — `load_dotenv()`
  does not override an already-set env var. Only the `ask`/`chat` commands need the key;
  `ingest`/`clean` work without it.
- Run the CLI with `PYTHONPATH=src python3 -m rag_mvp.cli <ingest|ask|chat|clean>`, or use
  the root shortcut scripts `ingest.py` / `ask.py` / `clean_db.py`.
- First `ingest`/`ask` downloads the embedding model (`all-MiniLM-L6-v2`) from the HuggingFace
  Hub, so the initial run needs network access and is slower than later runs.
- `ask`/`chat` require a built index: run `ingest` first or they error with "Vector database
  not found". `ingest` errors if `data/` has no `.pdf/.txt/.md` files. A sample incident
  document lives at `data/INC-2026-0001_callback_timeout.md`.
- `chroma_db/` (the persisted vector store) is git-ignored and rebuilt by `ingest`.

### Lint / test / build
- No linter, test suite, or build step is configured. For a quick syntax check use
  `python3 -m py_compile src/rag_mvp/*.py ingest.py ask.py clean_db.py`.
