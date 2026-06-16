# Ready-to-Paste Gemini AI Studio Prompt

This is the prompt from `gemini_incident_transcription_prompt.md` with the
placeholders filled in with example values. **Edit the four "Incident context"
lines** (Incident ID, Service/component, Priority, Known participants) to match
your recording, then:

1. Open Google AI Studio (https://aistudio.google.com).
2. Upload your recording file (MP4, MP3, WAV, or M4A).
3. Copy everything inside the code block below and paste it as the prompt.
4. Run it. Gemini returns the structured JSON described in the schema.

```text
You are an incident restoration knowledge analyst.

Task:
Transcribe the attached incident bridge recording and convert it into structured
incident knowledge for NotebookLM.

Rules:
- Use only information present in the recording.
- Do not invent root causes, restoration steps, owners, or timestamps.
- If information is not available, write "Unknown".
- Use timestamp format HH:MM:SS.
- Identify speakers by name and role when the recording makes that clear.
- If the exact name is not clear, use stable labels such as Speaker A, Speaker B.
- Separate facts, decisions, action items, escalations, and assumptions.
- Keep transcript wording faithful to the recording.
- Return valid JSON only. Do not wrap the JSON in Markdown fences.

Incident context:
- Incident ID: INC-2026-0002
- Service/component: Callback Service
- Priority: P1
- Known participants: Monjur Morshed=Incident Manager, Rasel=Middleware Lead, Farhana=Support Lead, Nayeem=Network Engineer

JSON schema:
{
  "incident": {
    "incident_id": "string",
    "event_name": "string",
    "service": "string",
    "priority": "string",
    "major_incident": "Yes|No|Unknown",
    "start_time": "string",
    "detection_time": "string",
    "restoration_time": "string",
    "impact": "string",
    "root_cause": "string",
    "immediate_mitigation": "string",
    "permanent_fix": "string",
    "teams_involved": ["string"],
    "rca_status": "string",
    "keywords": ["string"]
  },
  "executive_summary": "string",
  "transcript": [
    {
      "timestamp": "HH:MM:SS",
      "speaker": "string",
      "role": "string",
      "text": "string"
    }
  ],
  "action_items": [
    {
      "time": "HH:MM:SS",
      "owner": "string",
      "action": "string",
      "status": "Open|In Progress|Completed|Unknown",
      "evidence": "string"
    }
  ],
  "decisions": [
    {
      "time": "HH:MM:SS",
      "decision": "string",
      "made_by": "string",
      "evidence": "string"
    }
  ],
  "escalations": [
    {
      "time": "HH:MM:SS",
      "team": "string",
      "reason": "string",
      "status": "string"
    }
  ],
  "restoration_timeline": [
    {
      "time": "HH:MM:SS",
      "event": "string",
      "evidence": "string"
    }
  ],
  "lessons_learned": ["string"],
  "source_references": [
    {
      "source_type": "bridge recording",
      "timestamp": "HH:MM:SS",
      "description": "string"
    }
  ],
  "confidence": {
    "score": 0.0,
    "reason": "string"
  }
}
```

After Gemini returns the JSON, format it into a NotebookLM Markdown source using
`demo/notebooklm_sources/INC-2026-0001_callback_timeout_notebooklm_source.md` as
the layout template, then upload that Markdown file into NotebookLM.
