"""Premise-aware role prompting with the existing checked edit contracts.

This is a versioned treatment, not a formal certificate of natural-language
generalization. Exact kernel receipts and independent judgments are retained.
No role tool or learned artifact is made available to the non-ACE prover.
"""

from copy import copy
from dataclasses import fields
from typing import Any, override

import delphyne as dp
from delphyne.stdlib.environments import TemplatesManager
from delphyne.stdlib.policies import prompting_policy

from prove_ace_learning import (
    JudgeLearningEdit,
    ProposeLearningEdits,
    ReflectLearningRepairs,
    learning_examples,
)
from prove_grounded import grounded_search
from runtime.ace_role_journal import checkpoint_roles
from runtime.campaign_budget import CampaignResponsesModel
from runtime.campaign_pause import PauseAwareRoleModel
from runtime.model_registry import make_model
from runtime.replay_admission import admission_observer, recorded_prompt

REVIEW_GUIDANCE = """

Scope audit before approval:
1. Separate the exact local operation from a generalized mathematical rule.
   Read actual hypotheses and original versus introduced obligations. A
   successful numeral instance does not justify weaker premises or an
   unrestricted statement. Reject unsupported scope, stating the missing
   premise; an executable snippet alone is not sufficient.
2. Match every claim to its exact source context. A fact absent from that
   context, an open assertion, or evidence from a different obligation is
   not a proved repair. Unknown evidence remains unknown.
3. Decide novelty only after support. Compare the operation and its
   preconditions with the existing rules. Another application of an
   existing orientation, normalization, or positivity rule is an example,
   even if this is the first successful example in the supplied receipts.
4. A correction must address the old rule's actual failing operation.
   Retain valid old preconditions and preserve unrelated useful advice.
"""

WRITER_GUIDANCE = """

Preserve the current book and make only source-bound incremental edits.
Prioritize a recorded failure of an existing recipe over another redundant
example. Distinguish actual rejected operations from unknown or timed-out
checks. Do not discard useful local work because the theorem is unsolved.

Before generalizing a library operation, expose its actual type in the
exact source context (for example, pose proof of the lemma under a fresh
name). Keep every required premise in the proposed text. A checked example
at one numeral is not a proof of a universally weakened rule. A local
scope can be retained as an example when broader applicability is unproved.
Do not replace checked evidence by a persuasive rationale.

Use only the current c/d/r/b aliases. Preserve drafts and receipts when
stopping. On the final turn, return action-specific decisions; do not
request a tool after the tool allowance is exhausted.
"""

REFLECT_GUIDANCE = """

Compare the observed operation with the CURRENT book. Give priority to an
actual rejected instance of a current recipe and its narrow repair. Bind
the draft to the event whose checked prefix already introduces its names.
State its real hypotheses explicitly; do not infer weaker mathematical
premises from a successful numeral instance. Retain useful local repairs
even when the enclosing theorem remains open. Avoid extracting another
example of advice already covered unless it corrects a documented defect.
"""


class RoleTemplates(TemplatesManager):
    def __init__(self, original: TemplatesManager, guidance: bool) -> None:
        super().__init__(original.prompt_folders, original.data_manager)
        self.original, self.guidance = original, guidance

    @override
    def prompt(
        self,
        *,
        query_name: str,
        prompt_kind: str,
        template_args: dict[str, Any],
        default_template: str | None = None,
    ) -> str:
        text = self.original.prompt(
            query_name=query_name,
            prompt_kind=prompt_kind,
            template_args=dict(template_args),
            default_template=default_template,
        )
        if not self.guidance or prompt_kind != "system":
            return text
        query = template_args.get("query")
        if isinstance(query, JudgeLearningEdit):
            return text + REVIEW_GUIDANCE
        if isinstance(query, ProposeLearningEdits):
            return text + WRITER_GUIDANCE
        if isinstance(query, ReflectLearningRepairs):
            return text + REFLECT_GUIDANCE
        return text


@prompting_policy
def role_prompt[T](
    query: dp.AttachedQuery[T],
    env: dp.PolicyEnv,
    normal: dp.PromptingPolicy,
    guidance: bool,
) -> dp.StreamGen[T]:
    local = copy(env)
    local.templates = RoleTemplates(env.templates, guidance)
    yield from normal(query, local)


def sanitized_role_policy(
    snapshot_directory: str,
    pause_file: str,
    dollar_cap: float = 0.20,
    guidance: bool = True,
) -> dp.Policy[
    dp.Branch | dp.Compute | dp.Fail | dp.Message, dp.PromptingPolicy
]:
    original = make_model(
        "gpt-5.6-luna",
        for_tool_calls=True,
        api="responses",
        reasoning_effort="medium",
        convert_user_feedback_to_tool=True,
    )
    if not isinstance(original, CampaignResponsesModel):
        raise ValueError("Campaign accounting is required")
    original.halt_on_billing_issue, original.output_limit = True, 8192
    model = PauseAwareRoleModel(
        **{
            f.name: getattr(original, f.name)
            for f in fields(original)
            if f.init
        },
        pause_file=pause_file,
    )
    normal = dp.few_shot(
        model,
        max_requests=1,
        select_examples=learning_examples(),
        tag_user_feedback_messages=True,
    )
    limits = dict(price=dollar_cap, num_requests=7, rocq_seconds=180)
    return (
        dp.with_budget(dp.BudgetLimit(limits))
        @ admission_observer(limits)
        @ (
            (
                grounded_search()
                @ checkpoint_roles(snapshot_directory + "/checkpoints")
            )
            & role_prompt(
                recorded_prompt(normal, model, snapshot_directory), guidance
            )
        )
    )
