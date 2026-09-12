"""Offline corrections to six saved Sol-authored coverage examples.

These repair the observed training-only drafts, not deployment responses.
Every result must pass the ordinary Rocq checker before example admission.
Both harnesses use build-demos in experiments.coverage_experiment. No API.
"""

import runtime.pytanque_utils as pt


def repair_draft(index: int, script: str) -> str:
    tactics = pt.split_into_tactics(script)
    if index == 3:
        replacements = iter(
            (
                "- change (sum_f (fun k => 2 * k + 2) n + (2 * n + 2) = S n * S n + S n).",
                "- change (sum_f (fun k => 2 * k + 1) n + (2 * n + 1) = S n * S n).",
            )
        )
        tactics = [
            next(replacements) if t.strip() == "- simpl." else t
            for t in tactics
        ]
    elif index == 11:
        tactics = [
            t.replace(
                "Nat.lt_trans Hi (Nat.lt_succ_diag_r n)",
                "Nat.lt_trans i n (S n) Hi (Nat.lt_succ_diag_r n)",
            )
            for t in tactics
        ]
    elif index == 6:
        tactics = [
            t.replace(
                "norm_num.",
                "change (INR (S 48) = 49). repeat rewrite S_INR. simpl. lra.",
            )
            for t in tactics
        ]
    elif index == 19:
        tactics = [
            t.replace(
                "norm_num at h1 h2 h3 h4 h5 h6 h7 hd.",
                "cbv in h1, h2, h3, h4, h5, h6, h7, hd.",
            )
            for t in tactics
        ]
    return "\n".join(tactics)
