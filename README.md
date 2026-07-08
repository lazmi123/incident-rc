# LangChain + ChromaDB + Gemini RAG MVP

Clean, low-cost Retrieval-Augmented Generation (RAG) starter project.

Pipeline:

Documents -> Embeddings -> ChromaDB -> Retriever -> Gemini

## What this project includes

- Local document ingestion (`.pdf`, `.txt`, `.md`)
- Chunking with configurable size/overlap
- Local vector DB with ChromaDB (persisted on disk)
- Local embeddings using sentence-transformers (no paid embedding API required)
- Gemini for grounded answer generation
- Streamlit web app for upload + ask workflow
- Simple CLI (`ingest`, `ask`, `chat`, `clean`)

## 1) Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Copy environment file and add your Gemini API key:

```bash
cp .env.example .env
```

Set `GOOGLE_API_KEY` in `.env` from Google AI Studio.

## 2) Run the web app (upload + ask)

```bash
PYTHONPATH=src streamlit run web_app.py
```

In the browser app:
1. Choose a **Knowledge base name** (for example `incident-kb`)
2. Upload one or more files (`.pdf`, `.txt`, `.md`)
3. Click **Save files + Build index**
4. Ask questions with **Get answer**
5. See grounded source file names in the **Sources** section

The app persists data by knowledge base name:
- uploaded files are saved under `uploaded_data/<knowledge-base-name>/`
- Chroma vectors are saved under `uploaded_chroma/<knowledge-base-name>/`

When you open the app later and select the same knowledge base name,
it reuses the saved ChromaDB index and files.

## 3) Add documents

Put files in `data/`:

- `data/**/*.pdf`
- `data/**/*.txt`
- `data/**/*.md`

## 4) Build index (ingest)

Option A (CLI module):

```bash
PYTHONPATH=src python3 -m rag_mvp.cli ingest
```

Option B (shortcut script):

```bash
python3 ingest.py
```

Force full rebuild:

```bash
PYTHONPATH=src python3 -m rag_mvp.cli ingest --force-rebuild
```

## 5) Ask questions

One question:

```bash
PYTHONPATH=src python3 -m rag_mvp.cli ask "What happened during the incident?"
```

or

```bash
python3 ask.py "What happened during the incident?"
```

Interactive chat:

```bash
PYTHONPATH=src python3 -m rag_mvp.cli chat
```

or just:

```bash
python3 ask.py
```

## 6) Clean local vector DB

```bash
PYTHONPATH=src python3 -m rag_mvp.cli clean
```

or:

```bash
python3 clean_db.py
```

## Config

All config is environment-based (`.env`):

- `GOOGLE_API_KEY`: required for Gemini calls
- `GEMINI_MODEL`: default `gemini-2.5-flash`
- `EMBEDDING_MODEL`: default `sentence-transformers/all-MiniLM-L6-v2`
- `RAG_DATA_DIR`: default `data`
- `RAG_DB_DIR`: default `chroma_db`
- `RAG_TOP_K`: default `4`
- `RAG_CHUNK_SIZE`: default `800`
- `RAG_CHUNK_OVERLAP`: default `120`

## Notes

- This is an MVP starter optimized for local development and cost control.
- For large-scale production, consider managed retrieval infra and stronger observability.
