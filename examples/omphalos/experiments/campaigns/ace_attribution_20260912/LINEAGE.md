# Baseline lineage and the missing comparison

The premise that no non-ACE X benchmark existed is incorrect. The dedicated
`x_train_agentic` and `x_validation_agentic` archives each contain 40 problems
at two independently sampled replicate identifiers. Their cells are complete,
with no platform failures. Current dated token repricing gives:

| Historical non-ACE panel | Seed | Qualified solves | Cost |
|---|---:|---:|---:|
| trainX | 0 | 33/40 | $0.77731586 |
| trainX | 1 | 32/40 | $0.93246696 |
| validationX | 0 | 27/40 | $0.88696110 |
| validationX | 1 | 27/40 | $0.71897510 |

The study uses seed 0; the existence of seed 1 does not authorize another
fresh replicate. The current historical flagship references are trainX
28/40 at $0.68922336 and validationX 27/40 at $0.66722836. They are not a
controlled ACE ablation of the older baseline.

## Git archaeology

`3162a40c` (2026-08-24) is the immediate predecessor of `7bbb556f1`, the
commit that first adds `prove_ace.py` alongside the X study and platform
rebuild. Its code already documents Luna/core/medium as the recommendation
measured August 13. The canonical Luna command uses Responses, 32 turns,
and the original-partition $0.05 cap. The toolset rename lean→core was
prompt-neutral. A separate model or program revision called "Luna v2" was
not established; the verified claim is that the last pre-ACE source is
after the Luna migration.

The old source remains recoverable through Git and the existing
`prove_theorem_agentic` path. It is not restored over the flagship or
repurchased as a new experiment. The archived X configuration adds shown
definitions and the X-specific $0.10 budget to that lineage.

An exact [source snapshot](reference_source/prove_agentic_preace.py.txt)
and its Git/blob hash provenance are included for inspection. Commit
`7bbb556f1` was recorded September 1 and explicitly groups work from
August 24–27; its commit date is not the date adaptation first ran.

## Non-ACE differences that would confound a direct comparison

| Aspect | Historical X agentic baseline | Current bounded/focused flagship |
|---|---|---|
| Control loop | Generic agentic interaction | Grounded loop with focused reference/bridge/structure queries |
| Requests | 32 | 64 |
| Dollar allowance | $0.10 post-crossing stop | $0.10 with conservative pre-request admission |
| Verifier accounting | Assisted verification, without the new aggregate allowance | Per-operation limits and 300-second aggregate allowance |
| Tools | Core ReadSkill/SearchRocq | Adds bounded InspectProofState |
| Feedback | Assisted proof feedback | Typed outcome, bounded views and explicit verified prefix |
| Prompt | Generic proof proposal | Verified-state/operation instructions and focused decision |
| Definitions | Shown | Shown |
| Learned context | None | Frozen X3 book and conditional citation instructions |
| Runtime provenance | Earlier recorded platform | Later measured server profile |

The historical pre-X program additionally hid local definition preambles
and used the $0.05 original-partition cap. Those are not suitable settings
for the new X comparison. Definitions are retained in both new arms.

The new no-ACE control removes learned context from the current flagship
while holding the other rows fixed. This answers ACE's marginal value in
today's program. The old-to-new differences remain useful descriptive
evidence about the broader control architecture, with historical limits.

## Playbook provenance

The Luna incumbent is `ace_x3_offline.yaml`: 26 retained bullets, roughly
2103 estimated tokens, one shuffled trainX epoch, four-problem batches,
all four generative roles Luna/medium. Repriced generation cost was
$0.71110378; reflection $0.15074760; curation $0.04145398; reduction
$0.01361840. Total $0.91692376 before embeddings.

`ace_x3_strong.yaml` is not an all-Terra counterpart: its 40 generators
were Luna. Its Terra reflection/curation/reduction cost approximately
$2.08924000. It is useful historical evidence about role strength, but
does not replace the newly authorized all-Terra adaptation chain.

The attribution study preserves historical books and verdicts. Fresh Terra
training and the small cross-book experiment distinguish complete-pipeline
scaling from the contribution of using a stronger solver with fixed advice.
