"""Free train-only evidence export and real-Rocq contract checks.

Both harnesses: python -m tools.reports.resource_completion_evidence.
No model dispatch, book mutation, or historical rescoring occurs here.
"""

# ruff: noqa: E402 -- scope before experiment imports
from runtime.completion_scope import install

install()

from dataclasses import asdict
import json

from ace import ace_grounded as ag
from ace.ace_playbook import AddOp
from ace.ace_verified_snippets import SnippetBinding, SnippetWitness
from ace.terminal_evidence import TerminalEvidence, extract_terminal_evidence
from experiments.common.ace_pools import POOLS
from experiments.resource_completion_experiment import ROOT, accounting, save
from prove_evidence import BoundCurationDelta, protect_bound_delta
from runtime.tool_budget import ToolLimits


def main() -> None:
    if accounting()["receipts"]:
        raise ValueError("Offline evidence must precede paid execution")
    source = ROOT / "experiments/campaigns/ace_capacity_20260912"
    cells = json.loads((source / "creator_terminal_evidence.json").read_text())
    receipts: list[TerminalEvidence] = []
    for row in cells:
        directory = ROOT / row["source"]
        # Source metadata is train-only; never infer a partition from a path.
        theorem = directory.name.split("_generator_", 1)[1]
        receipt = extract_terminal_evidence(directory, theorem)
        assert receipt.status == "accepted"
        receipts.append(receipt)
    assert len(receipts) == 33
    save("terminal_receipts.json", [asdict(r) for r in receipts])
    selected = next(r for r in receipts if r.theorem_name == "amc12_2000_p6")
    accepted = ag.checked_proof(
        selected.problem_file,
        selected.theorem_name,
        list(selected.accepted_script),
        ToolLimits(),
        assisted=False,
    )
    proposed = ag.checked_proof(
        selected.problem_file,
        selected.theorem_name,
        list(selected.submitted_script),
        ToolLimits(),
        assisted=False,
    )
    assert accepted.feedback.success and not proposed.feedback.success
    assert selected.auto_finished and selected.accepted_tail

    witness = SnippetWitness(
        **json.loads((source / "snippet_witness.json").read_text())
    )
    candidate = json.loads((source / "snippet_verification.json").read_text())[
        "candidate"
    ]
    delta = BoundCurationDelta(
        "Keep a source-bound square nonnegativity example.",
        (AddOp("ADD", "Rocq", candidate),),
        (SnippetBinding(0, candidate, witness.identifier),),
    )
    protected = protect_bound_delta(
        delta, (witness,), (witness.identifier,), ToolLimits()
    )
    assert protected.bindings[0].text == witness.template
    assert protected.verdicts[0].decision == "source_preserved"
    # A subsequent reducer receives the retained binding, not the failed text.
    reduced = protect_bound_delta(
        BoundCurationDelta(
            "Retain the checked example",
            tuple(protected.delta.operations),
            protected.bindings,
        ),
        (witness,),
        (witness.identifier,),
        ToolLimits(),
    )
    assert reduced.verdicts[0].source_check.feedback.success
    assert reduced.bindings == protected.bindings
    save("snippet_curation_receipt.json", asdict(protected))
    save("snippet_reduction_receipt.json", asdict(reduced))
    problem, theorem = POOLS["trainX"]["mathd_numbertheory_48"]
    continuation = ag.checked_proof(
        problem,
        theorem,
        ["intros b Hb Heq.", "simpl in Heq."],
        ToolLimits(),
        assisted=True,
    )
    assert (
        continuation.feedback.success and continuation.feedback.auto_finished
    )
    save(
        "offline_evidence.json",
        dict(
            passed=True,
            paid_requests=0,
            terminal_receipts=len(receipts),
            nonidentical_terminal_scripts=sum(
                r.submitted_script != r.accepted_script for r in receipts
            ),
            accepted_proof_check=asdict(accepted),
            submitted_proof_check=asdict(proposed),
            snippet_source_preserved=True,
            snippet_survives_reduction=True,
            continuation=asdict(continuation),
            source_scores_unchanged=True,
            scope_note="Guard-denied legacy partition import read no data. Incidental legacy outcome comments in benchmark source were excluded from analysis.",
        ),
    )


if __name__ == "__main__":
    main()
