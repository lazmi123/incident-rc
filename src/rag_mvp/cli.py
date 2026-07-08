from __future__ import annotations

import argparse
import shutil
import sys

from dotenv import load_dotenv

from rag_mvp.config import load_settings
from rag_mvp.ingestion import ingest_documents
from rag_mvp.retrieval import answer_question


def cmd_ingest(force_rebuild: bool) -> None:
    settings = load_settings()
    doc_count, chunk_count = ingest_documents(settings, force_rebuild=force_rebuild)
    print(f"Ingested {doc_count} documents into {chunk_count} chunks.")
    print(f"Persisted Chroma DB at: {settings.db_dir}")


def cmd_ask(question: str) -> None:
    settings = load_settings()
    answer, docs = answer_question(settings, question)
    print("\nAnswer:\n")
    print(answer)

    print("\nSources:")
    if not docs:
        print("No matching chunks found.")
        return
    for idx, doc in enumerate(docs, start=1):
        print(f"{idx}. {doc.metadata.get('source', 'unknown')}")


def cmd_chat() -> None:
    print("Interactive RAG chat started. Type 'exit' to leave.")
    while True:
        question = input("\nAsk: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Bye.")
            return
        if not question:
            continue
        cmd_ask(question)


def cmd_clean() -> None:
    settings = load_settings()
    if settings.db_dir.exists():
        shutil.rmtree(settings.db_dir)
        print(f"Deleted vector DB at: {settings.db_dir}")
    else:
        print(f"No vector DB found at: {settings.db_dir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LangChain + ChromaDB + Gemini RAG MVP CLI"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ingest_parser = sub.add_parser("ingest", help="Ingest documents into Chroma DB")
    ingest_parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Delete existing DB directory before ingesting.",
    )

    ask_parser = sub.add_parser("ask", help="Ask one question")
    ask_parser.add_argument("question", help="Question to ask over indexed docs")

    sub.add_parser("chat", help="Start interactive chat")
    sub.add_parser("clean", help="Delete local Chroma DB directory")

    return parser


def main() -> None:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "ingest":
            cmd_ingest(force_rebuild=args.force_rebuild)
        elif args.command == "ask":
            cmd_ask(question=args.question)
        elif args.command == "chat":
            cmd_chat()
        elif args.command == "clean":
            cmd_clean()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
