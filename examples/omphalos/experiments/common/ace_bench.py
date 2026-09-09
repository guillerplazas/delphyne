"""
Experiment configuration for evaluating a frozen ACE playbook.

Kept OUT of `miniF2F_bench.py` on purpose: this config needs
`ace_playbook` (an omphalos-root module), and importing that from
`miniF2F_bench` would change the import requirements of every frozen
experiment script that does `import miniF2F_bench`. A separate module
keeps the frozen file byte-identical and the dependency local.

Follows the `ResponsesAgenticConfig` precedent: a *subclass* rather
than new fields on an existing config class, because `Experiment` keys
its stored per-config state on the config's field values — extending
an existing class would orphan every frozen run.
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import re
from collections.abc import Sequence
from dataclasses import dataclass

import experiments.common.miniF2F_bench as mf

import delphyne as dp


import experiments.common.minif2f_x as x  # noqa: E402

from ace.ace_playbook import Playbook  # noqa: E402
from ace.ace_triggers import (  # noqa: E402
    DEFAULT_MAX_HINTS,
    DEFAULT_SELECTION_RULE,
    TriggerTable,
)

_OMPHALOS_DIR = OMPHALOS_ROOT

ACE_ARM_RE = re.compile(
    r"^ace-(?P<sha>[0-9a-f]{8})(?:-k(?P<k>\d+))?-(?P<toolset>\w+)-(?P<effort>\w+)$"
)
"""
The arm segment of an ACE evaluation cell's directory name; the report
tools match on it, so `ace_config_name` and this regex move together.
"""

ACET_ARM_RE = re.compile(
    r"^acet-(?P<sha>[0-9a-f]{8})-(?P<tsha>[0-9a-f]{8})-k(?P<k>\d+)"
    r"(?:-r(?P<rule>\d+))?-(?P<toolset>\w+)-(?P<effort>\w+)$"
)
"""
The arm segment of a hint-on-error cell (`ACETriggeredConfig`): the
playbook sha, the trigger table sha and the hint cap. Deliberately not
matched by `ACE_ARM_RE`, so the frozen-playbook report tools never
mistake a triggered arm for a full-injection one.
"""


@dataclass
class ACEAgenticConfig(mf.ResponsesAgenticConfig):
    """
    The canonical agentic configuration plus a frozen playbook.

    `playbook_file` is a path relative to the omphalos root (kept
    under `experiments/playbooks/`, which — unlike
    `experiments/output/` — survives `make clean-experiments`).
    `playbook_sha256` pins the exact content: it is part of the config
    identity, so a re-adapted playbook can never silently reuse the
    frozen runs of an older one, and `instantiate` asserts the file
    still matches the hash it was measured with.

    `injection` selects how much of the playbook reaches the prompt:
    `"full"` renders every bullet (the paper's setting), `"top<k>"`
    (e.g. `"top8"`) renders only the k bullets with the highest
    helpful-minus-harmful score — the selective-injection idea from
    HINTS #38, which trades coverage for a smaller per-turn input tax.

    `render_version` picks the prompt rendering: 1 = the legacy
    `render_markdown` (ids and counters, placeholder when empty), 2 =
    `render_prompt` (ids only, empty string when empty so a cold cell
    is byte-identical to the baseline). `show_definitions` renders the
    problem file's own declarations (`pytanque_utils.parse_problem`).
    All three default to the values the 2026-08-24 evaluation runs
    were recorded with, so those configs keep their identity
    (`Experiment` excludes default-valued fields from it); X-partition
    arms set `render_version=2, show_definitions=True` explicitly.
    """

    playbook_file: str = ""
    playbook_sha256: str = ""
    injection: str = "full"
    render_version: int = 1
    show_definitions: bool = False

    def _problem(self) -> tuple[str, str]:
        # Original partitions first (frozen runs), then the X partitions.
        if self.bench_name in mf.ALL_PROBLEMS:
            return mf.ALL_PROBLEMS[self.bench_name]
        return x.ALL_X_PROBLEMS[self.bench_name]

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        args = super().instantiate(context)
        pb = Playbook.load(_OMPHALOS_DIR / self.playbook_file)
        assert pb.sha256() == self.playbook_sha256, (
            f"{self.playbook_file} does not match the hash this config"
            " was created with — the playbook drifted after the runs"
            " were recorded"
        )
        args.strategy = "prove_theorem_ace"
        args.policy = "prove_theorem_ace_policy"
        args.args["playbook"] = render_injection(
            pb, self.injection, self.render_version
        )
        args.args["show_definitions"] = self.show_definitions
        args.args["render_version"] = self.render_version
        return args


@dataclass
class ACETriggeredConfig(ACEAgenticConfig):
    """
    Hint on error (2026-09-05): the playbook is not rendered into the
    prompt at all; `prove_ace.prove_theorem_ace_triggered` attaches the
    bullets whose trigger matches each verifier rejection to that
    rejection's feedback. `triggers_file` / `triggers_sha256` pin the
    frozen, self-contained trigger table (`ace_triggers.TriggerTable`;
    it embeds the bullet contents and the playbook's sha, which must
    equal `playbook_sha256`); `max_hints` caps the bullets per
    feedback message. `injection` is `"triggered"` by construction and
    `render_version` is irrelevant (no playbook section is rendered).
    """

    triggers_file: str = ""
    triggers_sha256: str = ""
    max_hints: int = DEFAULT_MAX_HINTS
    selection_rule: int = DEFAULT_SELECTION_RULE
    """`ace_triggers.score` semantics (see `DEFAULT_SELECTION_RULE`);
    the x5 arm recorded rule 1, later arms set 2 explicitly."""

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        # The canonical agentic args, not `ACEAgenticConfig`'s: no
        # playbook is rendered (`render_injection` has no "triggered").
        args = super(ACEAgenticConfig, self).instantiate(context)
        pb = Playbook.load(_OMPHALOS_DIR / self.playbook_file)
        assert pb.sha256() == self.playbook_sha256, (
            f"{self.playbook_file} does not match the hash this config"
            " was created with — the playbook drifted after the runs"
            " were recorded"
        )
        text = (_OMPHALOS_DIR / self.triggers_file).read_text()
        table = TriggerTable.loads(text)
        assert table.sha256() == self.triggers_sha256, (
            f"{self.triggers_file} does not match the hash this config"
            " was created with — the trigger table drifted"
        )
        assert table.playbook_sha256 == self.playbook_sha256, (
            f"{self.triggers_file} was built for playbook "
            f"{table.playbook_sha256[:8]}, not {self.playbook_sha256[:8]}"
        )
        assert self.injection == "triggered", self.injection
        args.strategy = "prove_theorem_ace_triggered"
        args.policy = "prove_theorem_ace_triggered_policy"
        args.args["triggers"] = text
        args.args["max_hints"] = self.max_hints
        args.args["show_definitions"] = self.show_definitions
        if self.selection_rule != DEFAULT_SELECTION_RULE:
            args.args["selection_rule"] = self.selection_rule
        return args


def acet_config_name(cfg: ACETriggeredConfig, _uid: object) -> str:
    """`{bench}__acet-{sha8}-{tsha8}-k{K}-{toolset}-{effort}__{model}__seed{n}`."""
    rule = (
        ""
        if cfg.selection_rule == DEFAULT_SELECTION_RULE
        else f"-r{cfg.selection_rule}"
    )
    return (
        f"{cfg.bench_name}__acet-{cfg.playbook_sha256[:8]}"
        f"-{cfg.triggers_sha256[:8]}-k{cfg.max_hints}{rule}"
        f"-{cfg.toolset}-{cfg.reasoning_effort}"
        f"__{cfg.model_name}__seed{cfg.seed}"
    )


def ace_config_name(cfg: ACEAgenticConfig, _uid: object) -> str:
    """
    `{bench}__ace-{sha8}[-k{K}]-{toolset}-{effort}__{model}__seed{n}`.

    The sha8 is the playbook the cell ran with, so an online run — one
    playbook per step — is a set of arms that `ACE_ARM_RE` matches as
    a family, while a frozen-playbook evaluation is a single arm.
    """
    k = (
        ""
        if cfg.injection == "full"
        else f"-k{cfg.injection.removeprefix('top')}"
    )
    return (
        f"{cfg.bench_name}__ace-{cfg.playbook_sha256[:8]}{k}"
        f"-{cfg.toolset}-{cfg.reasoning_effort}"
        f"__{cfg.model_name}__seed{cfg.seed}"
    )


def render_injection(
    pb: Playbook, injection: str, render_version: int = 1
) -> str:
    """
    Render a playbook under an injection mode.

    `"full"` renders every bullet. `"top<k>"` keeps the k
    highest-scoring bullets by `helpful - harmful`, ties broken by
    insertion order (bullet id), so the choice is deterministic and
    reproducible from the stored playbook alone.
    """
    assert render_version in (1, 2, 3), render_version
    if injection == "full":
        selected = pb
    else:
        assert injection.startswith("top"), f"unknown injection {injection!r}"
        k = int(injection.removeprefix("top"))
        ranked = sorted(
            pb.bullets, key=lambda b: (-(b.helpful - b.harmful), b.id)
        )
        keep = {b.id for b in ranked[:k]}
        selected = Playbook(
            next_id=pb.next_id,
            bullets=[b for b in pb.bullets if b.id in keep],
        )
    if render_version == 1:
        return selected.render_markdown()
    return selected.render_prompt()


def render_cited(pb: Playbook, ids: Sequence[str], render_version: int) -> str:
    """
    The reference's Reflector input: only the bullets the Generator
    cited (`reflector_scope="cited"`), in playbook order, rendered like
    the Generator saw them. An empty citation set is said explicitly
    rather than rendered as an empty playbook, so the Reflector knows
    the Generator relied on nothing (and tags nothing).
    """
    wanted = {i for i in ids}
    cited = [b for b in pb.bullets if b.id in wanted]
    if not cited:
        return "(the generator cited no bullets)"
    header = (
        f"Only the bullets the generator cited are shown "
        f"({len(cited)} of {len(pb.bullets)}):\n"
    )
    sub = Playbook(next_id=pb.next_id, bullets=cited)
    body = (
        sub.render_markdown() if render_version == 1 else sub.render_prompt()
    )
    return header + body
