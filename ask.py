from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from dotenv import load_dotenv

from rag_mvp.cli import cmd_ask, cmd_chat


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Ask questions over your local RAG DB")
    parser.add_argument("question", nargs="*", help="Question to ask")
    args = parser.parse_args()

    if args.question:
        cmd_ask(" ".join(args.question))
    else:
        cmd_chat()
