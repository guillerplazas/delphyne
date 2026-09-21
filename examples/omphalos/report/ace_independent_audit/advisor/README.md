# Advisor report

Start with [report.pdf](report.pdf); the editable source is [report.md](report.md).
This brief includes completed eighty-attempt comparisons from the independent
campaign and one explicitly matched historical reset comparison, independently
audited in this campaign. It excludes pilot results and unmatched historical
comparisons as headline results.
Lower-budget numbers are labelled as replays of completed trajectories.

The figures and their coordinates are generated without API calls. From
`examples/omphalos`, either Codex or Claude Code can run:

```bash
python -m experiments.ace_independent_audit.advisor_report
```

The exporter checks input hashes against the original study manifest and
refuses incomplete or inexactly billed panels. It writes PDF, SVG and PNG
versions of both figures, plus `figure_data.json`. Original study artifacts
remain unchanged; this folder has its own additive review manifest.

From this folder, export the report:

```bash
pandoc report.md -o report.pdf --pdf-engine=xelatex -V papersize:a4 -V geometry:margin=0.65in -V fontsize=10pt -V 'mainfont:DejaVu Serif' -V 'monofont:DejaVu Sans Mono' -V colorlinks:true
```

`validation.json` records the data checks, document review and validation.
`manifest.json` records this addendum's file hashes. Regenerating a PDF can
change its metadata; a changed export requires a new review manifest.
