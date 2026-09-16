# ACE learning campaign: measured results

New API charges: **$2.94148562 / $30**; 1736 receipts, 0 unresolved.

Historical v2 controls: 40 trainX cells, 80 validationX cells. Validation is development data. Generator/controller unchanged; only learned books differ. No default promotion.

| Panel/arm | v2 solves | Candidate solves | v2 cost | Candidate cost | Solve p |
| --- | ---: | ---: | ---: | ---: | ---: |
| training/B | 28/40 | 30/40 | $0.685937 | $0.655461 | 0.6875 |
| validation/B | 48/80 | 47/80 | $1.528567 | $1.430224 | 1.0000 |

Every proof cell, including failures, is in [cells.csv](cells.csv). Raw-request and verifier evidence is indexed in [proof_cells.json](analysis/proof_cells.json). Family-clustered 90% intervals and cost tests are in [metrics.json](analysis/metrics.json); pilot judgments and role products are in [pilots.json](analysis/pilots.json).

[Mechanism](analysis/mechanism.json) lists retained edits with source receipts. [Economics](analysis/economics.json) separates preparation and uncached-token sensitivity. Exposure proves that a book was dispatched; it does not prove that a rule caused a solve.
