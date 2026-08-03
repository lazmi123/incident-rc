# PowerPoint ⇄ Excel Slide Sync

A small automation tool that takes a **previous PowerPoint deck** plus an
**updated Excel sheet** and produces a **new deck** where:

- Slides whose data changed in the spreadsheet are **fixed in place**
  (text, and table cells are refreshed, formatting is kept).
- Rows in the spreadsheet that don't have a matching slide yet get a
  **brand-new slide**, cloned from a template slide so it matches the
  deck's existing look and feel.
- Everything else in the original deck (title slides, section dividers,
  slides with no matching key, speaker notes, theme, layouts) is left
  untouched.

This is useful for decks that need to be regenerated every time a
tracking spreadsheet changes, e.g. a weekly incident/status review deck
driven by an incident tracker spreadsheet.

## How matching works

The tool never guesses which slide belongs to which spreadsheet row from
its visible text (that's fragile once the text itself has been
templated). Instead it uses a small marker hidden in the **speaker
notes** of each slide:

- A slide meant to be used as a blueprint for new slides has a note line
  `TEMPLATE: <template_name>`.
- A slide that was generated from a spreadsheet row has a note line
  `KEY: <row_key>`.

On every run:

1. The output deck starts as a full copy of the previous deck.
2. For every row in the spreadsheet (identified by a required `key`
   column):
   - If a slide already has `KEY: <key>` in its notes, its placeholders
     are refreshed from the row ("fix").
   - Otherwise, the slide named by the row's `template` column (or the
     first `TEMPLATE:` slide if the column is empty/omitted) is
     duplicated, its placeholders are filled from the row, and the new
     slide's notes get `KEY: <key>` so future runs can find and update
     it again ("create").
3. Placeholders are written in slide text, in table cells, and inside
   grouped shapes using the `{{column_name}}` syntax, where
   `column_name` matches a header in the spreadsheet.

## Spreadsheet format

The first row of the sheet is the header row. Two columns are special:

| column     | required | meaning                                                                 |
| ---------- | -------- | ------------------------------------------------------------------------ |
| `key`      | yes      | Stable unique id for the slide (e.g. an incident id). Used to detect updates vs. new slides across runs. |
| `template` | no       | Name of the `TEMPLATE:` slide to clone for new rows. Defaults to the first template slide found in the deck. |

All other columns are free-form and become available as `{{column}}`
placeholders on the matching slide.

## Usage

```bash
python -m pptx_excel_sync.sync_slides \
  --previous previous_deck.pptx \
  --excel updates.xlsx \
  --output new_deck.pptx
```

Optional flags:

- `--sheet NAME` – read a specific worksheet instead of the first one.
- `--dry-run` – print what would be updated/created without writing the
  output file.

The command prints a summary of which slides were updated, which were
created, and any placeholders that could not be filled (unknown column
or a template placeholder with no corresponding spreadsheet column).

## Try it with the bundled example

```bash
python pptx_excel_sync/examples/generate_samples.py
python -m pptx_excel_sync.sync_slides \
  --previous pptx_excel_sync/examples/previous_deck.pptx \
  --excel pptx_excel_sync/examples/updates.xlsx \
  --output /tmp/new_deck.pptx
```

The example deck has one incident slide already generated
(`KEY: INC-001`) whose status is stale, and the spreadsheet has an
updated status for `INC-001` plus a brand-new row `INC-002`. Running the
command above fixes the `INC-001` slide in place and appends a new slide
for `INC-002`, cloned from the `TEMPLATE: incident-status` slide.

## Running the tests

```bash
pip install -r pptx_excel_sync/requirements.txt
pytest pptx_excel_sync/tests
```
