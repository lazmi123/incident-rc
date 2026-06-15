# NotebookLM Demo Walkthrough

This demo uses a single synthetic incident source to show the target behavior.
The same structure is produced by `scripts/gemini_incident_transcriber.py` when
you run it against a real bridge recording.

## Demo steps

1. Open NotebookLM and create a notebook named
   `Incident Restoration Assistant Demo`.
2. Add this source:
   `demo/notebooklm_sources/INC-2026-0001_callback_timeout_notebooklm_source.md`
3. Ask NotebookLM the questions in `prompts/notebooklm_demo_questions.md`.
4. Confirm that each answer includes:
   - Similar incident used.
   - Transcript timestamps.
   - Restoration actions performed.
   - Teams involved.
   - Root cause or "Unknown" when not supported.
   - Confidence or source-reference wording.

## What a successful demo should show

- NotebookLM can answer questions about callback timeout incidents from the
  uploaded source.
- The response can cite transcript timestamps such as `00:01:05`, `00:12:20`,
  and `00:36:00`.
- The answer should not invent restoration procedures that are absent from the
  source.
- If a new symptom is not represented in the source, NotebookLM should say that
  no relevant incident history was found.
