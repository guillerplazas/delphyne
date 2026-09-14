# ACE retrospective

Start with **[reader_brief.pdf](reader_brief.pdf)**: the shorter personal
reading document, without citations. Its editable source is
[reader_brief.md](reader_brief.md).

For the advisor meeting use **[advisor_slides.pptx](advisor_slides.pptx)**
or the matching **[slide PDF](advisor_slides.pdf)**: **24 main slides and
seven question-led backups**. The expanded deck is self-contained and includes
the complete development-cycle tables, code mapping, explicit budget caps,
Luna/Terra conclusions and the 38/40 training result. Text, diagrams and table
cells are editable in PowerPoint; charts are embedded images with standalone
PDF/PNG versions in `advisor_figures/`. Edit `advisor_deck.yaml` to rebuild;
`advisor_slides.md` is the generated reading/export version.

The revised **[rehearsal guide](advisor_rehearsal.pdf)** includes a 15–20 minute
route, a complete discussion route and optional file visits by symbol.
For actual spoken wording, use the **[presentation script](advisor_script.pdf)**
or its editable [Markdown source](advisor_script.md): first-person text for
all 24 main slides, short answers for the seven backups, and silent stage cues.
Speaker notes are embedded in all 31 slides. The older `rehearsal_notes.*`
files describe the previous sixteen-slide presentation; the
[prepared excerpts](rehearsal_excerpts.md) remain useful evidence snapshots.
Copy [next_session_prompt.md](next_session_prompt.md) into a new Codex
session in Plan Mode for the proposed $30 experimental-budget follow-up.
That prompt keeps testX closed and prioritizes the whole Omphalos system.

The expanded deck includes the completed September 13 resource-completion
cycle alongside the audited September 12 evidence. It does not score ongoing
work in another session. No new measurements were purchased. The original
**report.pdf** remains the complete reference report. Editable narrative is in
`report.md`; generated appendices and bibliography are in `appendices.md`
and `sources.md`. All figures are supplied as PDF and PNG. `chart_data.xlsx`
contains the figure inputs, historical cells, campaign comparisons,
source inventory, and numerical checks; `data/` contains CSV/JSON equivalents.

`source_catalogue.md` indexes accessible narrative sources and large case
appendices. `implementation_index.md` is a static class/function guide.
Review depth and excluded mixed/protected sources are explicit in
`data/document_inventory.csv`. The record count is not a theorem count.

The report covers the full accessible ACE history through September 12,
2026. testX and protected challenge evidence stay closed. Existing
measurements are reused; the builder makes no model/API or Rocq calls.
Some historical archives are incomplete, and not all old preparation/retry
charges are recoverable. The report does not claim a complete research bill.

## Rebuild

Both Codex and Claude Code use the same shell commands, from
`examples/omphalos`. Required tools are the project's Python environment,
Matplotlib, PyYAML, Pandoc and XeLaTeX, with DejaVu fonts. The additional
workbook dependency is isolated from the project runtime:

```sh
python -m pip install --target report/ace_retrospective/.build/deps openpyxl==3.1.5
python -m tools.reports.ace_retrospective
```

To rebuild **only the expanded advisor deck and its rehearsal guide**, from
either Codex or Claude Code:

```sh
python report/ace_retrospective/build_advisor_deck.py
```

This uses installed Matplotlib, Pillow, PyYAML, Pandoc, XeLaTeX and LibreOffice.
All writes stay inside this report directory; no runtime or experiment module
is imported. The slide PDF is exported from the PowerPoint. LibreOffice gets
an isolated profile under `.build/advisor_v2/`.

The historical meeting builder can still rebuild the personal brief with
`python -m tools.reports.ace_meeting_materials --reader-only`. Its older
sixteen-slide rendering path is superseded by the dedicated deck builder;
do not use that path on the revised slide source.

If a harness sandbox blocks LibreOffice's runtime configuration, use
`--defer-slide-pdf` and approve the separate export command through that
harness's normal permission mechanism:

```sh
libreoffice --headless --convert-to pdf --outdir report/ace_retrospective report/ace_retrospective/advisor_slides.pptx
```

The default builder uses an isolated `-env:UserInstallation=file:///...`
profile; add an equivalent absolute profile path when exporting separately
if a LibreOffice session is already open. `--reader-only` rebuilds just
figures, excerpts, and the personal PDF. Source documents are not overwritten.
No benchmark modules or historical runners are imported.

For the original full-report builder, use `--data-only` to regenerate
figures, tables and workbook without PDF
rendering. The narrative is never overwritten by the builder. Generated
Markdown appendices, figures and tables are derived artifacts.

The explicit archive and campaign lists are in the builder. Numerical
inputs have SHA-256 hashes; each complete crossover group is checked
against its component cells and token repricing. The cumulative curves
include unsuccessful tasks in fixed partition-file order. Threshold
curves qualify already-observed final costs, rather than simulate an
unobserved budget policy. Continuation costs include their paid prefix once.

## Checks

```sh
python -m pytest -q tests/test_ace_retrospective.py
make test-coverage-cycle
# Check canonical symlinks directly while the memory index remains mixed.
ruff check tools/reports/ace_retrospective.py tests/test_ace_retrospective.py
```

Global partition/repricing commands are excluded because they can read
closed data. `verification.json` records the original report's checks,
PDF inspection and any pre-existing root type-check failures.

`advisor_verification.json` records the revised deck's input and output hashes,
numerical checks, slide/notes counts and layout review. `meeting_verification.json`
is the historical verification of the first adaptation and is superseded for
the revised presentation. It records the original derivative materials' input hashes,
numerical checks, page/slide counts, layout inspection and source-boundary
disclosure. The original report, workbook, and numerical evidence are retained.
The meeting-materials verification substitutes direct canonical symlink checks
for `make agents-check`, whose full memory-index read would cross the retained
source boundary.

The `.build/` folder contains temporary dependencies, rendering logs and
inspection images; it is not part of the deliverable. No commits are made
by this report task.
