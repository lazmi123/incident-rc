# Connect Recordings to Gemini Transcription and NotebookLM

This guide explains how recorded incident bridge videos become labelled
transcripts and how to connect the demo end to end.

## End-to-end flow

```text
Zoom/Teams recording
  -> local MP4/MP3/WAV/M4A file
  -> Gemini / Google AI Studio transcription
  -> structured JSON with speakers, timestamps, actions, and summary
  -> NotebookLM-ready Markdown source
  -> manual upload into NotebookLM
  -> ask incident restoration questions
```

## How transcription and labelling work

Gemini reads the audio track from the recording and follows the prompt in
`prompts/gemini_incident_transcription_prompt.md`.

The prompt asks Gemini to produce:

- timestamped transcript lines
- speaker names or stable speaker labels
- speaker roles when known
- incident summary
- restoration actions
- decisions
- escalations
- owners
- RCA/root-cause fields
- confidence and source references

Speaker labelling works best when you provide a participant list:

```text
Monjur Morshed=Incident Manager,
Rasel=Middleware Lead,
Farhana=Support Lead,
Nayeem=Network Engineer
```

If Gemini cannot confidently identify the real name, it should use labels such
as `Speaker A`, `Speaker B`, or `Unknown`.

## What you need

Required:

1. A Google AI Studio API key.
2. One recording file, for example:
   - MP4 from Zoom or Teams
   - MP3
   - WAV
   - M4A
3. Python 3.
4. NotebookLM access for manual source upload.

Optional but useful:

- RCA document
- Major incident report
- meeting minutes
- incident tracker export
- list of teams and service owners

## Step 1: Get the Google AI Studio API key

1. Open Google AI Studio.
2. Go to API keys.
3. Create or copy an API key.
4. Keep it private. Do not commit it to GitHub.

Set it in your terminal:

```bash
export GOOGLE_API_KEY="your-google-ai-studio-api-key"
```

## Step 2: Put the recording in the project

Create a local folder named `recordings` and put your file there:

```text
recordings/incident-bridge.mp4
```

The `recordings/` folder is ignored by Git so private videos are not committed.

## Step 3: Install the Python dependency

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Step 4: Run transcription and labelling

```bash
python scripts/gemini_incident_transcriber.py \
  recordings/incident-bridge.mp4 \
  --incident-id INC-2026-0002 \
  --service "Callback Service" \
  --priority P1 \
  --participants "Monjur Morshed=Incident Manager,Rasel=Middleware Lead" \
  --out demo/generated
```

Generated files:

```text
demo/generated/INC-2026-0002/incident_transcript.json
demo/generated/INC-2026-0002/notebooklm_source.md
```

Use the Markdown file for NotebookLM.

## Step 5: Upload into NotebookLM

1. Open NotebookLM.
2. Create a notebook, for example:

   ```text
   Incident Restoration Knowledge Base
   ```

3. Upload:

   ```text
   demo/generated/INC-2026-0002/notebooklm_source.md
   ```

4. Upload related RCA/MoM/incident report files if available.

## Step 6: Ask questions

Example:

```text
What happened in incident INC-2026-0002?
```

```text
What restoration actions were performed and who owned them?
```

```text
We are seeing HTTP 504 timeout from the bank callback endpoint. Based only on
uploaded incident history, what should we investigate first?
```

```text
List the transcript timestamps and sources used for your answer.
```

## Manual Google AI Studio option

If you do not want to run Python:

1. Open Google AI Studio.
2. Upload the recording file.
3. Paste the prompt from:

   ```text
   prompts/gemini_incident_transcription_prompt.md
   ```

4. Replace placeholders such as `{{incident_id}}`, `{{service}}`, and
   `{{participants}}`.
5. Run the prompt.
6. Copy the structured output into a Markdown source using the same section
   style as:

   ```text
   demo/notebooklm_sources/INC-2026-0001_callback_timeout_notebooklm_source.md
   ```

7. Upload the Markdown file into NotebookLM.

The Python script automates steps 2-6.

## Automatic Zoom or Teams download later

For this demo, manual download is the simplest and safest path.

If you later want automatic ingestion:

### Zoom

You need:

- Zoom account admin access.
- Zoom app credentials.
- Recording read permissions.
- Meeting ID or recording ID access.

### Microsoft Teams

You need:

- Microsoft Entra app registration.
- Microsoft Graph permissions for meeting recordings or the OneDrive/SharePoint
  location where recordings are stored.
- Admin consent from your organization.

After that, a downloader can save recordings into `recordings/`, and the same
Gemini script can process them.

## Important limitation

NotebookLM consumer does not currently provide a stable public API for automated
source upload. The demo therefore creates upload-ready files, and you upload
them manually. If your organization has NotebookLM Enterprise, source upload can
be automated through Google Cloud enterprise APIs.

## Recommended demo notebook setup

Use one notebook for related incidents:

```text
Incident Restoration Knowledge Base
```

Upload all approved generated incident sources into that notebook:

```text
INC-2026-0001 notebooklm_source.md
INC-2026-0002 notebooklm_source.md
INC-2026-0003 notebooklm_source.md
RCA documents
MoM notes
incident reports
```

This allows NotebookLM to compare incidents and answer similar-incident
questions from the uploaded source set.
