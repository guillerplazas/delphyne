# ACE platform revision: local repairs and reviewed book edits

The v2 implementation in `prove_ace_role_revision.py` and
`ace/role_revision.py` addresses failures exposed by the September 13
training artifacts. Work switched to platform development at Guille's
request; the old validation launch was stopped. Fifty-five scoped tests,
including real Rocq and campaign integration with HTTP blocked, passed
before the separately authorized
[rebenchmark](../experiments/campaigns/ace_revision_20260913/README.md).
The flagship and the measured v1 implementation remain unchanged.

## What the evidence required us to fix

The v1 writer pilot looked promising, but its automated book grew from
2103 to 3994 estimated tokens. Six of eight additions repeated existing
guidance, and all eight came from accepted training proofs. The failed
reflector also received misleading feedback when it mixed a local repair
with abstention. These are concrete interface and retention problems;
valid JSON and accepted snippets did not establish useful learning.

| Failure | v2 behavior | Offline check |
| --- | --- | --- |
| An unsolved theorem suppresses a useful local draft | `SubmitLocalRepair` binds an explicitly unverified draft to a training event; final disposition is separate | An unsolved AMC source supplies a checked helper-premise repair |
| Invalid final answers discard prior work | `ReflectionProduct` and `WriterProduct` retain drafts, receipts, contexts and diagnostics | Invalid reflector and curator finals preserve their inputs and checks |
| A budget stop never returns the role's product | Delphyne Message nodes checkpoint state before the next request | Request exhaustion returns no solution, yet the reducer recovers a checked repair without a new probe |
| Executable examples inflate the playbook | Reducer proposals receive a separate novelty review; examples remain outside the prompt | Duplicate and repeated-instance cases add no extra rule |
| Two proposals repeat one another within a batch | Each review sees earlier accepted edits; exact duplicates also fold deterministically | One add plus one example, with both evidence links retained |
| Faulty advice survives beside its correction | An update needs rejected and repaired snippets in the same exact context, plus an explicit correction judgment | The recorded INR `change` failure is corrected with a real-Rocq equality bridge |
| Cancellation leaves more requests running | A shared pause flag blocks subsequent role operations; admitted calls drain and settle | A pause during mocked transport retains the actual charge and blocks the next reservation |

The unsolved-source demonstration adds one 295-character operation, rather
than its whole source proof. This is a scripted mechanism demonstration,
not evidence that an LLM will find the repair or improve coverage.

## Roles and evidence

`ReflectLocalRepairs` sees authoritative terminal evidence and a compact
event index. `ReadTrainingEvidence` retrieves an exact recorded event.
`SubmitLocalRepair` saves its diagnosis, operation, preconditions and code;
it does not execute code. Final `done` means local drafts were submitted,
not that the theorem is complete. Conflicting abstention receives precise
field feedback. The final reason is retained in the product.

`ProposeBookEdits` gives curators and reducers `c`, `d`, `r` and `b` aliases
for contexts, drafts, receipts and book rules. `FindBookRules` performs
transparent lexical retrieval; it is not a semantic certificate.
`CheckAdviceSnippet` runs exact, unassisted Rocq fragments through Compute.
At most three new checks and 180 verifier seconds are available per role;
each check has a 60-second, 512-RPC and 8192-byte view allowance. Identical
checks reuse receipts. Changed snippets need a new check. Successor context
aliases allow a local fragment to be extended without claiming a new lemma.

Every draft receives an `add`, `update`, `example` or `drop` decision.
Updates preserve rule identity, section and helpful/harmful counters.
They require a logical rejection, not a resource or unknown outcome, and
an executed repair in the same context. A separate `JudgeBookEdit` query
checks the claimed relationship to the old advice. It sees the actual
snippets, source prefixes, errors and remaining goals, without the
proposer's persuasive rationale. Open assertions are not proved facts.
Duplicate judgments become evidence attachments; unsupported claims do
not change the book. Review failures preserve work for a later reducer.

`apply_product` revalidates the full decision/review trail. Whole-book and
target-content hashes reject stale edits. Unmentioned rules stay intact;
conflicting updates and over-budget batches fail without mutating the
original book. Rules have one paragraph and at most 700 characters; the
whole prompt has a 4000-token ceiling. Exact duplicate folding does not
increment helpfulness. `BookRevision` retains the old and new books, checked
evidence, reviews and applied rule IDs. `rule_examples` retrieves evidence
for a rule; only `revision.after.render_prompt()` goes to the generator.

Curator handoffs carry a compact plan/diagnostic summary; source contexts
and receipts are supplied once in their catalogue. They no longer repeat
the full product inside the evidence prose as well.

## Delphyne integration and recovery

The implementation uses strategies for contracts, Compute for Rocq,
Message for checkpoints, and a policy adapter for persistence. Policies
select the model, demonstrations and budget. This preserves the separation
described by [Delphyne](https://arxiv.org/abs/2502.05310); incremental book
edits address a mechanism of [ACE](https://arxiv.org/abs/2510.04618).

`role_revision_policy(snapshot_directory, pause_file, dollar_cap=0.20)`
requires the existing campaign ledger environment. It enforces its own
Delphyne dollar, seven-request and verifier limits. A writer gets four
proposal turns and at most three independent reviews; a reflector gets
four turns. The ledger remains the hard aggregate billing safeguard.

Use a separate snapshot directory for every role episode. Its `checkpoints/`
directory is an immutable, ordered journal. `RoleJournal.latest()` recovers
the last product, including a partial product when admission stopped the
strategy before it returned. `reduction_input` accepts those partial
products and original reflections. A complete reviewed reducer product is
required for application. Checkpoints run at Message nodes on cached replay
as well as live traversal; replay cannot roll the journal backwards or
silently substitute a different episode. The exact transport recorder is
unchanged.

To stop an upcoming campaign that uses the v2 policy, both harnesses use:

```bash
python -m runtime.campaign_pause /absolute/campaign/PAUSED --reason "platform review"
```

The command returns immediately. Let the existing supervised attempt drain;
an already admitted operation may still be waiting for ledger space or an
HTTP response. The flag does not kill processes and is not an automatic
resumption mechanism. The old v1 campaign did not use this adapter and
must not be resumed under its interrupted protocol.

## Reproduce offline

From `examples/omphalos`, with the development campaign's source fixtures:

```bash
source ~/.config/omphalos/env.sh
python -m tools.data.ace_role_revision_demos
pytest -q tests/test_ace_role_revision.py
```

Before sealing a new treatment, the builder regenerates scripted query demonstrations and
`platform_v2/demonstration.json`. It forbids HTTP and executes the local
repair with real Rocq. Tests cover invalid finals, budget exhaustion,
partial handoffs, within-batch deduplication, correction, stale edits,
prompt-size guards, cooperative cancellation, exact transport/checkpoint
replay and source-family exclusion. Role instructions are ordinary project
data in `prompts/ace/role_skills_v2/`, usable from either agent harness.

For the now-sealed `ace_revision_20260913` campaign, use the preserved
demonstrations and run the tests without regenerating them in place. New
Rocq timings can change fixture bytes even when rendered prompts match;
the measured source seal must remain intact.

## What still requires measurement

Semantic novelty and the connection between a rejected tactic and old
advice remain model judgments. Scripted tests establish enforcement and
recovery, not judgment quality or transfer. The new campaign counts new
operations and corrected rules separately from faithful abstention, and
reports unsolved-source yield, retained prompt tokens, checks, requests and
cost. Its complete paired flagship panels test transfer of the resulting
book; they do not isolate each tool's contribution. The censored v1
validation cells supply no verdict and were not mined to design these
changes.

Generator-side tool expansion remains lower priority: prior development
evidence did not justify another snippet/completion treatment, while the
adaptation failures above are directly demonstrated. The compact rule and
separate example representation leaves room for a separately evaluated
retrieval tool later. No generator tool change is bundled into this revision.

Accounting and the preserved v1 interpretation are in the
[campaign record](../experiments/campaigns/ace_roles_20260913/README.md).
The interrupted v1 campaign retains $1.98787940 in confirmed charges and a
$2.12898800 upper bound for unresolved requests, for $4.11686740 accounted.
Guille subsequently explicitly reset the experiment budget to zero and
authorized rebenchmarking after platform checks. The separate
`ace_revision_20260913` campaign therefore starts with a fresh $40 ceiling;
its authorization record preserves the earlier accounting. Neither ledger
is silently rewritten to erase charges or unresolved requests.

## Fresh benchmark outcome

The paid revision pass retained one new operation, one prerequisite
clarification from an unsolved source and six evidence-only examples. The
book has 27 rules and 2224 estimated tokens. Six partial curator products
expose remaining action-schema friction; their checked evidence survived.

Fresh training measured 28/40 candidate solves versus 29/40 for the
flagship. Two-seed validation measured 48/80 versus 47/80, at 1.6% lower
inference cost. The differences are inconclusive and miss the registered
practical threshold. Preparation cost $0.45092992; the whole fresh campaign
cost $4.92990612. The flagship default remains in place. See the
[findings](../experiments/campaigns/ace_revision_20260913/FINDINGS.md) for
paired uncertainty, all-in economics and the scope of each mechanism claim.
