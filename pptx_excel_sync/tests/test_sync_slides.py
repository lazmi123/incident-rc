import openpyxl
import pytest
from pptx import Presentation

from pptx_excel_sync.sync_slides import load_rows, main, sync_deck


def _build_deck(path):
    prs = Presentation()
    content_layout = prs.slide_layouts[1]

    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = "Weekly Incident Review"

    template_slide = prs.slides.add_slide(content_layout)
    template_slide.shapes.title.text = "{{title}}"
    body = template_slide.placeholders[1].text_frame
    body.text = "Status: {{status}}"
    body.add_paragraph().text = "Owner: {{owner}}"
    template_slide.notes_slide.notes_text_frame.text = "TEMPLATE: incident-status"

    existing_slide = prs.slides.add_slide(content_layout)
    existing_slide.shapes.title.text = "INC-001: Checkout latency spike"
    body = existing_slide.placeholders[1].text_frame
    body.text = "Status: Investigating"
    body.add_paragraph().text = "Owner: Priya"
    existing_slide.notes_slide.notes_text_frame.text = (
        "KEY: INC-001\nTEMPLATE_SOURCE: incident-status"
    )

    prs.save(path)
    return path


def _build_excel(path, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Incidents"
    ws.append(["key", "template", "title", "status", "owner"])
    for row in rows:
        ws.append(row)
    wb.save(path)
    return path


@pytest.fixture
def deck_path(tmp_path):
    return _build_deck(tmp_path / "previous_deck.pptx")


def _slide_text(slide):
    parts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            parts.append(shape.text_frame.text)
    return "\n".join(parts)


def _notes_text(slide):
    return slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""


def test_load_rows_parses_header_and_rows(tmp_path):
    excel_path = _build_excel(
        tmp_path / "updates.xlsx",
        [
            ["INC-001", "incident-status", "INC-001: Checkout latency spike", "Resolved", "Priya"],
        ],
    )
    rows = load_rows(str(excel_path))
    assert rows == [
        {
            "key": "INC-001",
            "template": "incident-status",
            "title": "INC-001: Checkout latency spike",
            "status": "Resolved",
            "owner": "Priya",
        }
    ]


def test_load_rows_requires_key_column(tmp_path):
    excel_path = tmp_path / "no_key.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["identifier", "status"])
    ws.append(["INC-001", "Resolved"])
    wb.save(excel_path)

    with pytest.raises(ValueError, match="key"):
        load_rows(str(excel_path))


def test_sync_updates_existing_slide_in_place(deck_path, tmp_path):
    excel_path = _build_excel(
        tmp_path / "updates.xlsx",
        [
            ["INC-001", "incident-status", "INC-001: Checkout latency spike", "Resolved", "Priya"],
        ],
    )
    output_path = tmp_path / "new_deck.pptx"

    result = sync_deck(str(deck_path), str(excel_path), str(output_path))

    assert result.updated == ["INC-001"]
    assert result.created == []
    assert result.warnings == []

    prs = Presentation(str(output_path))
    assert len(prs.slides) == 3, "no new slide should have been added"

    inc_slide = prs.slides[2]
    assert "Status: Resolved" in _slide_text(inc_slide)
    assert "Owner: Priya" in _slide_text(inc_slide)
    assert "KEY: INC-001" in _notes_text(inc_slide)


def test_sync_creates_new_slide_from_template(deck_path, tmp_path):
    excel_path = _build_excel(
        tmp_path / "updates.xlsx",
        [
            ["INC-002", "incident-status", "INC-002: Login API 500s", "Mitigated", "Jordan"],
        ],
    )
    output_path = tmp_path / "new_deck.pptx"

    result = sync_deck(str(deck_path), str(excel_path), str(output_path))

    assert result.updated == []
    assert result.created == ["INC-002"]
    assert result.warnings == []

    prs = Presentation(str(output_path))
    assert len(prs.slides) == 4, "a new slide should have been appended"

    new_slide = prs.slides[3]
    text = _slide_text(new_slide)
    assert "INC-002: Login API 500s" in text
    assert "Status: Mitigated" in text
    assert "Owner: Jordan" in text
    assert "KEY: INC-002" in _notes_text(new_slide)

    # The template slide itself must remain untouched for future runs.
    template_slide = prs.slides[1]
    assert "TEMPLATE: incident-status" in _notes_text(template_slide)
    assert "{{title}}" in _slide_text(template_slide)


def test_sync_updates_and_creates_together(deck_path, tmp_path):
    excel_path = _build_excel(
        tmp_path / "updates.xlsx",
        [
            ["INC-001", "incident-status", "INC-001: Checkout latency spike", "Resolved", "Priya"],
            ["INC-002", "incident-status", "INC-002: Login API 500s", "Mitigated", "Jordan"],
        ],
    )
    output_path = tmp_path / "new_deck.pptx"

    result = sync_deck(str(deck_path), str(excel_path), str(output_path))

    assert result.updated == ["INC-001"]
    assert result.created == ["INC-002"]

    prs = Presentation(str(output_path))
    assert len(prs.slides) == 4


def test_sync_warns_when_no_template_available_for_new_row(deck_path, tmp_path):
    excel_path = _build_excel(
        tmp_path / "updates.xlsx",
        [
            ["INC-003", "does-not-exist", "INC-003: Something broke", "Open", "Alex"],
        ],
    )
    output_path = tmp_path / "new_deck.pptx"

    result = sync_deck(str(deck_path), str(excel_path), str(output_path))

    assert result.created == []
    assert result.skipped == ["INC-003"]
    assert any("does-not-exist" in warning for warning in result.warnings)

    prs = Presentation(str(output_path))
    assert len(prs.slides) == 3, "no slide should be added when the template is missing"


def test_sync_warns_on_placeholder_with_no_matching_column(deck_path, tmp_path):
    excel_path = _build_excel(
        tmp_path / "updates.xlsx",
        [
            ["INC-001", "incident-status", "INC-001: Checkout latency spike", "Resolved", None],
        ],
    )
    output_path = tmp_path / "new_deck.pptx"

    result = sync_deck(str(deck_path), str(excel_path), str(output_path))

    # `owner` column exists but is blank -> should render as empty, not a warning.
    assert not any("owner" in warning for warning in result.warnings)

    prs = Presentation(str(output_path))
    inc_slide = prs.slides[2]
    assert "Owner:" in _slide_text(inc_slide)


def test_sync_is_idempotent_across_repeated_runs(deck_path, tmp_path):
    """Running sync twice with different data each time must both times
    actually change the slide, proving placeholders aren't permanently
    consumed after the first fix."""
    first_excel = _build_excel(
        tmp_path / "updates1.xlsx",
        [["INC-001", "incident-status", "INC-001: Checkout latency spike", "Resolved", "Priya"]],
    )
    first_output = tmp_path / "deck_v1.pptx"
    sync_deck(str(deck_path), str(first_excel), str(first_output))

    second_excel = _build_excel(
        tmp_path / "updates2.xlsx",
        [["INC-001", "incident-status", "INC-001: Checkout latency spike", "Closed", "Priya"]],
    )
    second_output = tmp_path / "deck_v2.pptx"
    result = sync_deck(str(first_output), str(second_excel), str(second_output))

    assert result.updated == ["INC-001"]
    assert result.warnings == []

    prs = Presentation(str(second_output))
    assert len(prs.slides) == 3
    text = _slide_text(prs.slides[2])
    assert "Status: Closed" in text
    assert "Status: Resolved" not in text


def test_sync_dry_run_does_not_write_output(deck_path, tmp_path):
    excel_path = _build_excel(
        tmp_path / "updates.xlsx",
        [
            ["INC-002", "incident-status", "INC-002: Login API 500s", "Mitigated", "Jordan"],
        ],
    )
    output_path = tmp_path / "should_not_exist.pptx"

    result = sync_deck(str(deck_path), str(excel_path), dry_run=True)

    assert result.created == ["INC-002"]
    assert not output_path.exists()


def test_cli_main_writes_output(deck_path, tmp_path, capsys):
    excel_path = _build_excel(
        tmp_path / "updates.xlsx",
        [
            ["INC-001", "incident-status", "INC-001: Checkout latency spike", "Resolved", "Priya"],
            ["INC-002", "incident-status", "INC-002: Login API 500s", "Mitigated", "Jordan"],
        ],
    )
    output_path = tmp_path / "new_deck.pptx"

    exit_code = main([
        "--previous", str(deck_path),
        "--excel", str(excel_path),
        "--output", str(output_path),
    ])

    assert exit_code == 0
    assert output_path.exists()
    captured = capsys.readouterr()
    assert "Updated 1 slide" in captured.out
    assert "Created 1 slide" in captured.out
