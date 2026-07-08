from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from dotenv import load_dotenv

from rag_mvp.cli import cmd_ingest


if __name__ == "__main__":
    load_dotenv()
    cmd_ingest(force_rebuild=False)
