# Execution notes

The initial source/data seal and protocol are preserved. Supplemental
amendment 01 records a dependency correction after 80 new Luna proof
cells and four Terra training generators had completed.

The original citation helper called the general challenge exclusion
function, which attempted to read the protected challenge manifest.
The installed Python audit hook raised PermissionError before the read.
No protected contents were returned and no testX access occurred.
The completed generator batch cost $0.465317 over 33 requests. Total
settled new API spend at the interruption was $2.06003972, with no
unknown charges or active requests.

The correction accepts the explicitly authorized trainX allowlist
without opening the challenge manifest. Other theorem names retain the
original exclusion check and fail closed under the development guard.
The amendment verifier preserves the original seal, chains old/new hashes,
and adds this formerly unsealed helper dependency to the checked files.
Seventeen attribution tests passed before resuming. A further regression
test checks seal preservation, source drift, and a false amendment history.

The resume uses completed immutable batch markers. No proof episodes or
API calls from the first batch were repeated. The original failing exit
file is retained as campaign.exit; the resumed process writes
campaign.resume_01.exit. Both sessions append to campaign.log.

The additional admission probe is offline explanatory analysis. It replays
all observed responses and restores cumulative output-token allowance.
The opaque reasoning-reference serialization was not saved, so the probe
omits those bytes and calculates a lower bound on the next reservation.
When even that lower bound exceeds remaining money, rejection is proven.
The probe never dispatches HTTP or answers an unobserved request. On Luna,
all 53 unsolved histories replayed: 38 prove a monetary rejection, nine
remain indeterminate under this lower-bound test, and six return without
a next model request after spending 240.8–264.4 verifier seconds, leaving
less than the required 60-second operation reservation. This measures the
current controller's constraints, not unrestricted model capacity.


An offline content probe checked Terra's early `rocq-00001` square-bound
advice on its trainX source environment. Its `have hs : ... := Rle_0_sqr _`
syntax fails; replacing it with the ordinary `assert ... by apply Rle_0_sqr`
proves the same source theorem. The learned book remains unchanged. This is
an applicability defect, despite the lemma name itself being available.

A separate feedback audit reproduced incomplete-Qed errors with empty
reported goals. On amc12b_2002_p3, `Show.` exposes four unfocused goals;
on imo_1960_p2 it exposes the remaining nonzero-denominator side condition.
`Show Existentials.` confirms both. The bounded inspection command allowlist
currently excludes `Show`; pagination over the focused list cannot reveal
these obligations. This is now open hint #128, with no runtime or prompt
change in the attribution experiment. Both audits use only already exposed
trainX/validationX states and make zero API calls.


The broader Luna reference audit extracts identifiers inside every backtick
code span, including names embedded in longer snippets. It checks 39
bullet/reference pairs. All candidate names locate in at least one source
batch environment except `R_scope`; `Print Scope R_scope.` confirms that
this is a valid scope rather than a missing global constant. The earlier
single-identifier-span audit is retained as v1; v2 reuses its checks and
adds the previously missed snippets. This illustrates why these checks
are diagnostics, not an automatic content-quality score.

The main scoped suite passed 52 tests after amendment 01; the additional
reference-extraction regression also passes (53 tests in the combined set).
Pinned Pyright passes the new campaign, helper and test modules. The touched
legacy adaptation module has exactly the same 21 diagnostics as checkpoint
23329b09; the before/after multiset is saved in
adaptation_typecheck_comparison.json. Pinned root Pyright still reports the
17 existing find_invariants/why3py diagnostics. No unrelated source changed.


Amendment 02 was registered before any diagnostic panel began. The initial
$4 swap and $6 effort allocations were enough for anticipated actual
charges but not necessarily for all simultaneous maximum-output reservations
at 24-worker capacity. The batch entry now transfers completed Terra-main
slack to swaps and completed-swap slack to effort through the existing
idempotent ledger operation. This follows the protocol's forward-slack rule;
no individual budget, concurrency, model, prompt, seed or cell count changes.
The new child entry point supports the already running coordinator. The
original seal and both amendment hash links remain intact. Pinned Pyright
passes the modified runner, and the existing ledger tests cover ceiling
preservation, idempotence and unresolved-charge rejection.


The resumed campaign completed with exit 0: all 312 new proof episodes,
90 additional generative preparation jobs, and 25 embedding requests. The
3939 receipts settle to $38.88507492, with no unresolved charges, missing
cells, administrative censoring, or exported platform-failed cells. Operation
memory/transport failures inside completed trajectories remain in diagnostics.
No explicit infrastructure retry episode was needed.

Both diagnostic-stage transfers occurred as registered in amendment 02.
The exact runner after amendment 01 and the amendment 02 source delta are
retained alongside the amendment records. Final source/data verification
passes without changing the original seal.

Final offline analysis replays all 89 unsolved main histories: 57 sufficient
monetary rejections, 24 indeterminate lower bounds, eight returns after less
than a full operation allowance remains. All observed responses replay.
Reference audits cover all final-book candidate names; the bad Terra snippet
survives, but no per-cell score difference is attributed to it solely because
it appears in the book. Full scope and limitations are in RESULTS.md.

The first scoped generic-reprice CLI invocation discovered only immediate
child runs (the 32 diagnostic configurations). Its log is retained as
reprice_shallow_discovery.log. The final inventory-driven repricer names all
seven exact runs, checks 402 generative configurations and separately adds
25 embedding receipts. All prices reproduce exactly. This is an offline
analysis correction; no paid result or price was rewritten.

Final checks: 53 scoped tests, new-code pinned Pyright, Ruff, and dual-harness
invariants pass. Root Pyright retains 17 existing outside-scope diagnostics;
the touched legacy adaptation module retains an identical multiset of 21.
Verification logs, inventory, receipt export, and complete report are staged
with the study; raw caches/SQLite/event logs remain local and frozen.
