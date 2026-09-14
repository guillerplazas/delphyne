---
name: omphalos-ace-platform-first
description: "ACE platform correctness before paid runs; explicit fresh $40 authorization on 2026-09-13"
metadata:
  node_type: memory
  type: feedback
---

On 2026-09-13, Guille stopped the first ACE role campaign's validation
launch and asked for more platform work before experiments. The small
validity/utility pilot was insufficient reason to rush to benchmarking:
the observed loss of local repairs and redundant book growth required
implementation fixes first. Preserve that sequencing in future work.

After the v2 changes, Guille explicitly authorized restarting experiments
with experimental spend reset to zero, then reiterated that the platform
must work correctly before dispatch. The fresh $40 authorization belongs
to `ace_revision_20260913`; it does not erase the old campaign's ledger.
The earlier `ace_roles_20260913` validation is administratively censored,
must not resume, and provides no comparison verdict. Its partial outcomes
were not used to tune v2. Authorization and old accounting are linked in
the new campaign's `authorization.json`.

The platform and campaign integration preflight passed 55 scoped tests,
including real Rocq, budget-stop recovery, exact replay, and matched proof
request behavior. See [[omphalos-ace-retrospective]] and
`../docs/ace_role_revision.md`. Correctness checks establish the mechanism;
the paid campaign separately measures model behavior and book transfer.

The fresh proof benchmark is complete. Its interpretation and exact spend
are in `../experiments/campaigns/ace_revision_20260913/FINDINGS.md`; use that
record rather than mixing it with the earlier censored campaign. Platform
correctness, useful learning yield, statistical support and a default change
are separate decisions. The source seal also covers the executable
demonstrations: run the preserved tests, but do not regenerate those
fixtures in place after sealing.
