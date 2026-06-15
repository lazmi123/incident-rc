#!/usr/bin/env python3
"""Transcribe an incident recording with Gemini and render a NotebookLM source.

The script is intentionally small: it uploads a local audio/video file to Gemini,
asks for structured incident knowledge, saves the JSON response, and writes a
Markdown file that can be uploaded into NotebookLM.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "gemini-2.5-flash"

PROMPT_TEMPLATE = """You are an incident restoration knowledge analyst.

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
- Incident ID: {incident_id}
- Service/component: {service}
- Priority: {priority}
- Known participants: {participants}

JSON schema:
{{
  "incident": {{
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
  }},
  "executive_summary": "string",
  "transcript": [
    {{
      "timestamp": "HH:MM:SS",
      "speaker": "string",
      "role": "string",
      "text": "string"
    }}
  ],
  "action_items": [
    {{
      "time": "HH:MM:SS",
      "owner": "string",
      "action": "string",
      "status": "Open|In Progress|Completed|Unknown",
      "evidence": "string"
    }}
  ],
  "decisions": [
    {{
      "time": "HH:MM:SS",
      "decision": "string",
      "made_by": "string",
      "evidence": "string"
    }}
  ],
  "escalations": [
    {{
      "time": "HH:MM:SS",
      "team": "string",
      "reason": "string",
      "status": "string"
    }}
  ],
  "restoration_timeline": [
    {{
      "time": "HH:MM:SS",
      "event": "string",
      "evidence": "string"
    }}
  ],
  "lessons_learned": ["string"],
  "source_references": [
    {{
      "source_type": "bridge recording",
      "timestamp": "HH:MM:SS",
      "description": "string"
    }}
  ],
  "confidence": {{
    "score": 0.0,
    "reason": "string"
  }}
}}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe an incident bridge recording and render a NotebookLM source."
    )
    parser.add_argument("recording", type=Path, help="Local audio/video file path.")
    parser.add_argument("--incident-id", required=True, help="Incident identifier.")
    parser.add_argument("--service", default="Unknown", help="Service or component name.")
    parser.add_argument("--priority", default="Unknown", help="Incident priority.")
    parser.add_argument(
        "--participants",
        default="Unknown",
        help='Comma-separated names and roles, e.g. "Monjur=Incident Manager,Rasel=Middleware".',
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini model name.")
    parser.add_argument(
        "--api-key-env",
        default="GOOGLE_API_KEY",
        help="Environment variable that contains the Google AI Studio API key.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("demo/generated"),
        help="Output directory for generated JSON and Markdown.",
    )
    return parser.parse_args()


def import_gemini_sdk() -> tuple[Any, Any]:
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: install it with `pip install -r requirements.txt`."
        ) from exc
    return genai, types


def wait_for_file_ready(client: Any, uploaded_file: Any, timeout_seconds: int = 600) -> Any:
    """Wait until the Gemini File API finishes processing the uploaded media."""
    deadline = time.time() + timeout_seconds
    current = uploaded_file

    while time.time() < deadline:
        state = getattr(current, "state", None)
        state_name = getattr(state, "name", None) or str(state or "")
        state_name = state_name.upper()

        if "FAILED" in state_name:
            raise RuntimeError(f"Gemini file processing failed: {state_name}")
        if "PROCESSING" not in state_name:
            return current

        time.sleep(5)
        current = client.files.get(name=current.name)

    raise TimeoutError("Timed out waiting for Gemini to process the uploaded file.")


def extract_json(response_text: str) -> dict[str, Any]:
    text = response_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def generate_incident_json(args: argparse.Namespace) -> dict[str, Any]:
    if not args.recording.exists():
        raise SystemExit(f"Recording not found: {args.recording}")

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(
            f"Set {args.api_key_env} with a Google AI Studio API key before running."
        )

    genai, types = import_gemini_sdk()
    client = genai.Client(api_key=api_key)

    prompt = PROMPT_TEMPLATE.format(
        incident_id=args.incident_id,
        service=args.service,
        priority=args.priority,
        participants=args.participants,
    )

    print(f"Uploading {args.recording} to Gemini Files API...", file=sys.stderr)
    uploaded = client.files.upload(file=str(args.recording))
    uploaded = wait_for_file_ready(client, uploaded)

    print(f"Generating structured transcript with {args.model}...", file=sys.stderr)
    response = client.models.generate_content(
        model=args.model,
        contents=[uploaded, prompt],
        config=types.GenerateContentConfig(
            audio_timestamp=True,
            response_mime_type="application/json",
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return extract_json(response.text)


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def cell(value: Any) -> str:
    if value in (None, ""):
        return "Unknown"
    text = str(value).replace("\n", " ").strip()
    return text.replace("|", "\\|")


def bullet_list(items: list[Any]) -> str:
    if not items:
        return "- Unknown"
    return "\n".join(f"- {cell(item)}" for item in items)


def render_notebooklm_source(data: dict[str, Any]) -> str:
    incident = data.get("incident", {})
    confidence = data.get("confidence", {})
    incident_id = cell(incident.get("incident_id", "Unknown"))
    title = cell(incident.get("event_name", "Incident bridge transcript"))

    lines = [
        f"# NotebookLM Source: {incident_id} {title}",
        "",
        "> Generated from an incident bridge recording. Review and approve this",
        "> source before using it for operational restoration guidance.",
        "",
        "## Source metadata",
        "",
        f"- Source type: Incident bridge transcript",
        f"- Incident ID: {incident_id}",
        f"- Event name: {title}",
        f"- Service: {cell(incident.get('service'))}",
        f"- Priority: {cell(incident.get('priority'))}",
        f"- Major incident: {cell(incident.get('major_incident'))}",
        f"- Incident start time: {cell(incident.get('start_time'))}",
        f"- Detection time: {cell(incident.get('detection_time'))}",
        f"- Restoration time: {cell(incident.get('restoration_time'))}",
        f"- RCA status: {cell(incident.get('rca_status'))}",
        "",
        "## Executive summary",
        "",
        cell(data.get("executive_summary")),
        "",
        "## Mandatory incident fields",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Incident ID | {incident_id} |",
        f"| Event Name | {title} |",
        f"| Service | {cell(incident.get('service'))} |",
        f"| Priority | {cell(incident.get('priority'))} |",
        f"| Major Incident | {cell(incident.get('major_incident'))} |",
        f"| Impact | {cell(incident.get('impact'))} |",
        f"| Root Cause | {cell(incident.get('root_cause'))} |",
        f"| Immediate Mitigation | {cell(incident.get('immediate_mitigation'))} |",
        f"| Permanent Fix | {cell(incident.get('permanent_fix'))} |",
        f"| Teams Involved | {cell(', '.join(as_list(incident.get('teams_involved'))))} |",
        f"| RCA Status | {cell(incident.get('rca_status'))} |",
        f"| Keywords | {cell(', '.join(as_list(incident.get('keywords'))))} |",
        "",
        "## Labelled transcript",
        "",
        "| Timestamp | Speaker | Role | Transcript |",
        "| --- | --- | --- | --- |",
    ]

    for segment in as_list(data.get("transcript")):
        if not isinstance(segment, dict):
            continue
        lines.append(
            "| {timestamp} | {speaker} | {role} | {text} |".format(
                timestamp=cell(segment.get("timestamp")),
                speaker=cell(segment.get("speaker")),
                role=cell(segment.get("role")),
                text=cell(segment.get("text")),
            )
        )

    lines.extend(
        [
            "",
            "## Restoration timeline",
            "",
            "| Time | Event | Evidence |",
            "| --- | --- | --- |",
        ]
    )
    for item in as_list(data.get("restoration_timeline")):
        if not isinstance(item, dict):
            continue
        lines.append(
            f"| {cell(item.get('time'))} | {cell(item.get('event'))} | {cell(item.get('evidence'))} |"
        )

    lines.extend(
        [
            "",
            "## Action items",
            "",
            "| Time | Owner | Action | Status | Evidence |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in as_list(data.get("action_items")):
        if not isinstance(item, dict):
            continue
        lines.append(
            "| {time} | {owner} | {action} | {status} | {evidence} |".format(
                time=cell(item.get("time")),
                owner=cell(item.get("owner")),
                action=cell(item.get("action")),
                status=cell(item.get("status")),
                evidence=cell(item.get("evidence")),
            )
        )

    lines.extend(
        [
            "",
            "## Decisions",
            "",
            "| Time | Decision | Decision owner | Evidence |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in as_list(data.get("decisions")):
        if not isinstance(item, dict):
            continue
        lines.append(
            "| {time} | {decision} | {made_by} | {evidence} |".format(
                time=cell(item.get("time")),
                decision=cell(item.get("decision")),
                made_by=cell(item.get("made_by")),
                evidence=cell(item.get("evidence")),
            )
        )

    lines.extend(
        [
            "",
            "## Escalations",
            "",
            "| Time | Team | Reason | Status |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in as_list(data.get("escalations")):
        if not isinstance(item, dict):
            continue
        lines.append(
            "| {time} | {team} | {reason} | {status} |".format(
                time=cell(item.get("time")),
                team=cell(item.get("team")),
                reason=cell(item.get("reason")),
                status=cell(item.get("status")),
            )
        )

    lines.extend(
        [
            "",
            "## Lessons learned",
            "",
            bullet_list(as_list(data.get("lessons_learned"))),
            "",
            "## Mandatory source citation block",
            "",
            f"- Similar incident used: {incident_id}",
            f"- Transcript references: {cell(', '.join(ref.get('timestamp', 'Unknown') for ref in as_list(data.get('source_references')) if isinstance(ref, dict)))}",
            f"- RCA reference: {cell(incident.get('rca_status'))}",
            f"- Confidence score: {cell(confidence.get('score'))}",
            f"- Confidence reason: {cell(confidence.get('reason'))}",
            "",
            "## Grounding instruction for NotebookLM",
            "",
            "When answering from this source, cite the incident ID and transcript",
            "timestamps. If no matching evidence appears in this source or other",
            "uploaded approved incident sources, state that no relevant incident",
            "history was identified.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(data: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "incident_transcript.json"
    markdown_path = out_dir / "notebooklm_source.md"

    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    markdown_path.write_text(render_notebooklm_source(data))

    print(f"Wrote {json_path}", file=sys.stderr)
    print(f"Wrote {markdown_path}", file=sys.stderr)


def main() -> int:
    args = parse_args()
    incident_out = args.out / args.incident_id
    data = generate_incident_json(args)
    write_outputs(data, incident_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
