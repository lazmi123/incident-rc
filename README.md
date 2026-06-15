# Incident Recording AI Demo

This repository is a lightweight demo for converting incident bridge recordings
into searchable, source-grounded incident knowledge for NotebookLM. It is scoped
to the requirement brief: no custom platform, no dashboard, and no production
ingestion pipeline. The demo focuses on:

- AI transcription from Zoom, Teams, audio, or video recordings.
- Speaker-labelled transcript segments with timestamps.
- Restoration actions, decisions, escalations, owners, and status extraction.
- A structured incident summary that can be uploaded to NotebookLM.
- Prompt packs for Google AI Studio/Gemini and NotebookLM.
- Source citation discipline: answers should only be based on retrieved incident
  history.

## Repository contents

```text
demo/
  notebooklm_sources/
    INC-2026-0001_callback_timeout_notebooklm_source.md
prompts/
  gemini_incident_transcription_prompt.md
  notebooklm_demo_questions.md
scripts/
  gemini_incident_transcriber.py
requirements.txt
```

## Quick demo without any integration

1. Open NotebookLM.
2. Create a notebook named `Incident Restoration Assistant Demo`.
3. Upload the Markdown file in `demo/notebooklm_sources/`.
4. Ask the questions from `prompts/notebooklm_demo_questions.md`.

The sample source already contains the labelled transcript, restoration summary,
action items, and references that NotebookLM can cite.

## Process a real recording with Google AI Studio/Gemini

Install the optional Python dependency:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set a Google AI Studio API key:

```bash
export GOOGLE_API_KEY="your-google-ai-studio-api-key"
```

Run the transcriber on an MP4, WAV, MP3, or M4A recording:

```bash
python scripts/gemini_incident_transcriber.py \
  recordings/incident-bridge.mp4 \
  --incident-id INC-2026-0002 \
  --service "Callback Service" \
  --priority P1 \
  --participants "Monjur Morshed=Incident Manager,Rasel=Middleware Lead" \
  --out demo/generated
```

The script writes:

- `incident_transcript.json` - structured transcript and extracted fields.
- `notebooklm_source.md` - upload-ready NotebookLM source.

Upload `notebooklm_source.md` into NotebookLM with any RCA, MoM, incident report,
or tracker export for the same incident.

## What you need to connect or provide

To run this demo on your own incident recordings, provide:

1. **Google AI Studio / Gemini access**
   - A `GOOGLE_API_KEY` from Google AI Studio, or
   - Vertex AI project details if your organization requires enterprise Google
     Cloud access instead of AI Studio.
2. **Incident recordings**
   - Zoom or Microsoft Teams recording files, preferably MP4, MP3, WAV, or M4A.
   - If you want automated download later, provide Zoom/Teams API access. For
     this demo, local files are enough.
3. **NotebookLM access**
   - A Google account that can create NotebookLM notebooks and upload sources.
   - NotebookLM consumer currently does not provide a stable public upload API,
     so this demo produces files that are uploaded manually.
   - If you have NotebookLM Enterprise, provide the Google Cloud project,
     location, and service account/IAM details for API-based notebook/source
     management.
4. **Historical incident documents**
   - RCA documents, major incident reports, MoM notes, tracker exports, known
     workaround documents, and service ownership references.
5. **Metadata dictionaries**
   - Participant roster with names, roles, and teams.
   - Service/component names, incident priorities, incident types, and common
     error code patterns.

Do not commit secrets or private recordings to this repository. Keep credentials
in environment variables or your organization's secret manager.
