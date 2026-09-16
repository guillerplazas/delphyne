"""Post-run offline inspection of each registered role opportunity.

This analysis never changes measured strategies/prompts or dispatches HTTP.
It checks raw draft code without repairing it. Results are observations of
local execution, not automatic semantic novelty labels.
"""

# ruff: noqa: E402
from runtime.ace_learning_scope import install

install()

from dataclasses import asdict
from typing import Any
from unittest.mock import patch

from delphyne.utils.typing import pydantic_load

from ace.learning_contracts import observe_local_progress
from ace.role_revision import ReflectionProduct, WriterProduct
from ace.rocq_snippets import check_snippet
from experiments import ace_learning_experiment as c
from runtime.campaign_budget import CampaignResponsesModel


def reflection(which: str) -> None:
    c.activate("pilots", events=False)
    jobs = {j.bench_name: j for j in c.all_configs() if j.arm == "reflection"}
    for row in c.read("pilot_registration.json")["cases"]:
        if row["treatment"] != "reflection":
            continue
        path = f"analysis/reflection_checks/{which}_{row['case']}.json"
        if (c.CAMPAIGN / path).exists():
            continue
        product = (
            pydantic_load(ReflectionProduct, row["original"])
            if which == "old"
            else c.role_product(jobs[row["case"]])
        )
        assert isinstance(product, ReflectionProduct)
        contexts = {ctx.identifier: ctx for ctx in product.contexts}
        checks: list[dict[str, Any]] = []
        for draft in product.drafts:
            with patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("Offline audit forbids HTTP"),
            ):
                receipt = check_snippet(
                    contexts[draft.context_id],
                    draft.proposed_code,
                    dict(seconds=60, rpc_calls=512, view_bytes=8192),
                )
                observation = observe_local_progress(
                    receipt, dict(seconds=10, rpc_calls=128, view_bytes=8192)
                )
            checks.append(
                dict(
                    draft=asdict(draft),
                    receipt=asdict(receipt),
                    receipt_id=receipt.identifier,
                    observation=asdict(observation),
                )
            )
        c.save(
            path,
            dict(
                which=which,
                theorem=row["case"],
                product_status=product.status,
                checks=checks,
                paid_calls=0,
            ),
        )
        print(
            row["case"],
            which,
            [
                (r["receipt"]["status"], r["observation"]["outcome"])
                for r in checks
            ],
            flush=True,
        )


def curation() -> None:
    c.activate("pilots", events=False)
    jobs = {j.bench_name: j for j in c.all_configs() if j.arm == "curation"}
    for row in c.read("pilot_registration.json")["cases"]:
        if row["treatment"] != "curation":
            continue
        for which in ("old", "new"):
            path = f"analysis/curation_checks/{which}_{row['case']}.json"
            if (c.CAMPAIGN / path).exists():
                continue
            product = (
                pydantic_load(WriterProduct, row["original"])
                if which == "old"
                else c.role_product(jobs[row["case"]])
            )
            assert isinstance(product, WriterProduct)
            checks: list[dict[str, Any]] = []
            for receipt in product.receipts:
                with patch.object(
                    CampaignResponsesModel,
                    "_send_final_request",
                    side_effect=AssertionError("Offline audit forbids HTTP"),
                ):
                    check = check_snippet(
                        receipt.context,
                        receipt.snippet,
                        dict(seconds=60, rpc_calls=512, view_bytes=8192),
                    )
                    if check.identifier != receipt.identifier:
                        raise ValueError(
                            "Curator receipt did not recheck exactly"
                        )
                    observation = observe_local_progress(
                        receipt,
                        dict(seconds=10, rpc_calls=128, view_bytes=8192),
                    )
                checks.append(
                    dict(
                        receipt_id=receipt.identifier,
                        observation=asdict(observation),
                    )
                )
            c.save(
                path,
                dict(
                    which=which,
                    theorem=row["case"],
                    product=asdict(product),
                    checks=checks,
                    paid_calls=0,
                ),
            )


if __name__ == "__main__":
    import sys

    if sys.argv[1] == "curation":
        curation()
    else:
        reflection(sys.argv[1])
