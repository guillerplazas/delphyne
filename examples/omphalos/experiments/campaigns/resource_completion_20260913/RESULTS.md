# Resource-completion results

A changes only the enforced output cap to 4096; B evaluates the existing corrected structured continuation. The frozen book is unchanged.

| Panel | Arm | Qualified solves | Total cost | Cost/solve |
|---|---|---:|---:|---:|
| training | Historical reference | 28/40 | $0.689223 | $0.024615 |
| training | A | 30/40 | $1.017078 | $0.033903 |
| training | B | 25/40 | $0.730437 | $0.029217 |
| validation | Historical reference | 27/40 | $0.667228 | $0.024712 |
| validation | A | 26/40 | $1.128138 | $0.043390 |
| validation | B | 23/40 | $0.737946 | $0.032085 |

New experimental cost: **$3.61359998 of $30**; 2156 receipts; 0 unresolved. No new adaptation, embeddings or writing roles. Codex-session charges unavailable.

Follow-up selection: `None`. Practical gates and adjusted coverage p-values are in selection.json. Detailed paired costs, 90% intervals, exposure and failures are in reports/ and diagnostics/.

ValidationX is repeatedly reused development data. Seed-0 controls are historical; cache discounts, tariff, runtime and controller conditions limit comparisons. Any selected follow-up is exploratory after selection. No default changed and no frozen score was revised.

Cache sensitivity (same recorded tokens and registered tariff):

| Panel | Arm | Cached input | Tariff cost | Without cache discount |
|---|---|---:|---:|---:|
| training | Historical reference | 66.4% | $0.689223 | $1.257519 |
| training | A | 60.5% | $1.017078 | $1.802047 |
| training | B | 68.2% | $0.730437 | $1.433787 |
| validation | Historical reference | 75.9% | $0.667228 | $1.469747 |
| validation | A | 74.9% | $1.128138 | $2.646722 |
| validation | B | 75.4% | $0.737946 | $1.712665 |

This repricing does not simulate a different admission policy. The hard reservations use uncached input prices in every arm. Seed labels identify separately cached repeated executions; Responses supplies no provider seed guarantee. Historical controls used their archived runtime; all fresh arms use the capacity campaign's pinned profile.
