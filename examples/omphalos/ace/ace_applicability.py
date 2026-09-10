"""Syntax-only applicability contracts; shared by both agent harnesses.

The grammar guard constrains proposals, but never applies a text rewrite.
Only a live kernel check at the original prefix can admit a correction.
"""

from dataclasses import dataclass
import re
from typing import Literal

from ace.ace_grounded import Checked, Outcome, checked_proof
import runtime.pytanque_utils as pt
from runtime.tool_budget import ToolLimits

Pattern = Literal["change", "set", "nra", "unsupported"]
Mode = Literal["R", "Q", "F", "A"]


@dataclass(frozen=True)
class RepairState:
    problem_file: str
    theorem_name: str
    prefix: tuple[str, ...]
    failed_action: str
    error: str
    outcome: Outcome
    goals: tuple[str, ...]
    environment: str


@dataclass(frozen=True)
class RepairDecision:
    decision: Literal["repair", "abstain"]
    pattern: Pattern
    correction: str
    reason: str


@dataclass(frozen=True)
class RepairExample:
    id: str
    state: RepairState
    answer: RepairDecision
    source_cell: str
    source_sha256: str
    source_index: int


def syntax_form(tactic: str) -> tuple[Pattern, str]:
    """A deliberately finite grammar, not an arbitrary tactic translator."""
    change = re.fullmatch(r"(\s*(?:\{\s*)?)change (.+)\.", tactic)
    if change:
        lead, term = change.groups()
        location = ""
        located = re.fullmatch(r"(.+) in ([A-Za-z_][\w']*)", term)
        if located:
            term, name = located.groups()
            location = f" in {name}"
        return "change", f"{lead}change ({term}){location}."
    binding = re.fullmatch(
        r"(\s*(?:[-+*]+\s*|\{\s*)?)set ([A-Za-z_][\w']*) := (.+)\.",
        tactic,
    )
    if binding:
        lead, name, term = binding.groups()
        return "set", f"{lead}set ({name} := {term})."
    bracket = re.search(r"\bnra \[([^\[\];]+)\]", tactic)
    if bracket:
        expressions = [s.strip() for s in bracket[1].split(",")]
        if any(not s or any(c in s for c in "{}\n") for s in expressions):
            return "unsupported", ""
        # Existing hypotheses need no reintroduction. Lemma applications do.
        poses = [
            f"pose proof ({s}); "
            for s in expressions
            if not re.fullmatch(r"[A-Za-z_][\w']*", s)
        ]
        replacement = "".join(poses) + "nra"
        if poses and re.search(r"\bby\s*$", tactic[: bracket.start()]):
            replacement = f"({replacement})"
        return "nra", tactic[: bracket.start()] + replacement + tactic[
            bracket.end() :
        ]
    return "unsupported", ""


def eligible(state: RepairState) -> bool:
    return (
        state.outcome == "rejected"
        and "Syntax error" in state.error
        and syntax_form(state.failed_action)[0] != "unsupported"
    )


def syntax_tokens(text: str) -> tuple[str, ...]:
    """Ignore whitespace between tokens, never inside names or strings.

    Comments are outside the registered syntax fragment. Keep multi-character
    operators and quoted strings whole so whitespace cannot alter a token.
    """
    if "(*" in text or "*)" in text:
        return ("unsupported-comment", text)
    return tuple(
        re.findall(
            r'"(?:""|[^"])*"|[\w]+[\w\']*|:=|<=|>=|<>|->|<-|=>|[^\s]',
            text,
        )
    )


def supported_decision(state: RepairState, answer: RepairDecision) -> bool:
    pattern, correction = syntax_form(state.failed_action)
    return (
        eligible(state)
        and answer.decision == "repair"
        and answer.pattern == pattern
        and syntax_tokens(answer.correction) == syntax_tokens(correction)
    )


def signature(state: RepairState) -> tuple[Pattern, str, str]:
    """Route by grammar, target location and state domain, never theorem ID."""
    pattern, _ = syntax_form(state.failed_action)
    location = (
        "hypothesis"
        if re.search(r" in [\w']+\.$", state.failed_action)
        else "goal"
    )
    if pattern == "set":
        domain = "binding"
    elif pattern == "nra":
        domain = (
            "real-arithmetic"
            if any(re.search(r"\bR\b", g) for g in state.goals)
            else "unsupported"
        )
    else:
        domain = (
            "proposition"
            if re.search(r"[=<>]", state.failed_action)
            else "unsupported"
        )
    return pattern, location, domain


def error_shape(error: str) -> str:
    match = re.search(r"Syntax error: (.+?)(?:\\n|'\))", error)
    return match[1] if match else error


def select_ids(
    state: RepairState, bank: tuple[RepairExample, ...], mode: Mode
) -> tuple[str, ...]:
    if mode in ("R", "Q"):
        return ()
    if mode == "F":
        return tuple(e.id for e in bank)
    if not eligible(state):
        return ()
    pattern, _, domain = signature(state)
    target = re.search(r" in ([\w']+)\.$", state.failed_action)
    if target and not any(
        re.search(rf"\b{re.escape(target[1])}\s*:", g) for g in state.goals
    ):
        return ()
    candidates = [
        e
        for e in bank
        if (
            e.state.environment == state.environment
            or pattern in ("change", "set")  # Rocq grammar, no imported lemma
            or (
                "Reals" in e.state.environment and "Reals" in state.environment
            )
        )
        and signature(e.state)[0] == pattern
        and error_shape(e.state.error) == error_shape(state.error)
        and signature(e.state)[2] == domain
    ]
    # Goal and hypothesis changes share a proposition grammar. The query
    # retains the actual target; kernel conversion is checked there.
    positives = [e for e in candidates if e.answer.decision == "repair"]
    negatives = [e for e in candidates if e.answer.decision == "abstain"]
    return tuple(e.id for e in positives[:1] + negatives[:1])


def check_repair(
    state: RepairState,
    answer: RepairDecision,
    limits: ToolLimits = ToolLimits(),
) -> Checked:
    if not supported_decision(state, answer):
        return Checked(
            pt.Feedback(
                False,
                0,
                "unsupported correction",
                "Outside registered syntax grammar.",
            ),
            "rejected",
            0,
            0,
            "",
        )
    return checked_proof(
        state.problem_file,
        state.theorem_name,
        [*state.prefix, *pt.split_into_tactics(answer.correction)],
        limits,
        assisted=False,
    )


def executed(
    state: RepairState, answer: RepairDecision, checked: Checked
) -> bool:
    extended = [*state.prefix, *pt.split_into_tactics(answer.correction)]
    return (
        supported_decision(state, answer)
        and checked.outcome in ("accepted", "incomplete")
        and checked.feedback.proof_so_far == extended
    )


def checked_application(
    state: RepairState, correction: str, limits: ToolLimits
) -> Checked:
    """Same assisted verifier as the reference; record only real computations."""
    from runtime.admission_events import record

    checked = checked_proof(
        state.problem_file,
        state.theorem_name,
        [*state.prefix, *pt.split_into_tactics(correction)],
        limits,
    )
    record(
        "syntax_repair",
        "checked",
        outcome=checked.outcome,
        original_prefix=list(state.prefix),
        correction=correction,
        prefix=checked.feedback.proof_so_far,
        goals=checked.feedback.remaining_goals,
    )
    return checked
