# AGENTS.md

## Cursor Cloud specific instructions

This repository is a small, self-contained **Python 3 CLI demo** (no server, no
web UI, no build step). The product converts an incident bridge recording into a
structured transcript and a NotebookLM-ready Markdown source. The only runtime
component is `scripts/gemini_incident_transcriber.py`; standard usage is
documented in `README.md` and `docs/connect_recordings_to_notebooklm.md`.

### Service overview
- **Single service**: the `gemini_incident_transcriber.py` CLI. There is nothing
  to "serve" or keep running.

### Running / lint / test / build
- The only dependency is `google-genai` (`requirements.txt`); the update script
  installs it. `import google.genai` works from system Python after that.
- There is **no linter, test suite, or build step** configured. Use
  `python -m py_compile scripts/gemini_incident_transcriber.py` as a syntax/lint
  check.
- A full CLI run (`python scripts/gemini_incident_transcriber.py <recording> --incident-id ...`)
  calls the live Gemini Files + `generate_content` APIs, so it requires both a
  local audio/video recording file **and** a `GOOGLE_API_KEY` (Google AI Studio
  key). Without the key the script exits early with a clear message; without a
  recording file it errors that the file is not found.
- To exercise the core render path **without** the Gemini API, import the
  module functions directly (`extract_json` -> `render_notebooklm_source` ->
  `write_outputs`) and feed sample incident JSON.

### Gotchas
- The base image's Python lacks `ensurepip`, so `python3 -m venv` fails until
  `python3.12-venv` is installed. Installing dependencies with the system `pip`
  (what the update script does) works without a virtualenv, so a venv is
  optional.
- Generated output lands in `demo/generated/` (and `recordings/` for inputs),
  both of which are git-ignored.
