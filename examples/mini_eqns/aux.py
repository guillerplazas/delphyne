"""
Interactive baseline for the *mini-eqns* benchmark.

Key points
----------
* Uses `dp.interact` so the LLM can refine its proof after checker
  feedback – no manual chat‑history handling required.
* All prompts are rendered by Delphyne from the standard Jinja templates
  (see  prompts/ProveEqualityQuery.*.jinja ).
* The search‑policy               =  loop() @ dfs(...)
  The prompting‑policy            =  few_shot(model, …)
  together form a complete “oracular program” ready for experiments.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import delphyne as dp
from delphyne import Branch, Computation, Strategy, dfs, strategy

import checker as ch  # domain‑specific proof checker
# ---------------------------------------------------------------------
# 1) Query  ── ask the LLM for ONE proof attempt
# ---------------------------------------------------------------------


@dataclass
class ProveEqualityQuery(dp.Query[dp.Response[str, dp.Never]]):
    """
    One turn in the interaction loop.

    Parameters
    ----------
    equality : ch.Eq
        The target equality  (lhs == rhs)  to prove.
    prefix   : str
        Chat history propagated by `dp.interact` (initially "").

    The three Jinja templates that live in *prompts/* are
      · ProveEqualityQuery.system.jinja
      · ProveEqualityQuery.instance.jinja
      · ProveEqualityQuery.repair.jinja
    Delphyne discovers them automatically – nothing to wire by hand.
    """

    equality: ch.Eq
    prefix: str = ""

    # Allow few‑shot YAML blocks to be parsed automatically
    __parser__: ClassVar = dp.yaml_from_last_block

    # Globals available inside the templates
    def globals(self) -> dict[str, object]:
        return {"rules": ch.TRIG_RULES}

    # ── Parsing ──────────────────────────────────────────────────────
    # We keep the raw text.  Validation happens in the `process` part
    # of dp.interact.
    def parse(self, answer: dp.Answer) -> dp.Response[str, dp.Never]:
        assert isinstance(answer.content, str)
        return dp.Response(text=answer.content, prefix=answer.content)


# ---------------------------------------------------------------------
# 2) Checker wrapper – callable through `dp.compute`
# ---------------------------------------------------------------------


def _check_proof(eq: ch.Eq, proof_txt: str) -> ch.CheckResult | ch.ProofError:
    """
    Call the domain checker.

    Returns either
      • a success object (subclass of CheckResult)      OR
      • a ProofError  with diagnostics (which Delphyne
        routes to *.repair.jinja* for the next turn).
    """
    return ch.check(eq, proof_txt, ch.TRIG_RULES)


# ---------------------------------------------------------------------
# 3) Strategy – interactive proof‑search
# ---------------------------------------------------------------------


@strategy
def prove_equality_interactive(
    equation: ch.Eq,
) -> Strategy[Branch | Computation, dp.PromptingPolicy, ch.Proof]:
    """
    Repeatedly ( Query → Checker ) until the proof is accepted.

    The surrounding *search policy* (see builder below) decides how many
    feedback cycles are allowed before the run is considered a failure.
    """

    # `dp.interact` wires {step, process} into one feedback loop
    proof_txt = yield from dp.interact(
        # ① generate next proof attempt
        step=lambda pref, _: ProveEqualityQuery(equation, pref).using(
            dp.ambient_pp
        ),
        # ② check it
        process=lambda resp, _: _check_proof(equation, resp.text).using(
            dp.just_compute
        ),
    )

    # On success, parse the YAML into a *typed* ch.Proof object
    proof: ch.Proof = dp.yaml_from_last_block(ch.Proof, proof_txt)
    return proof


# ---------------------------------------------------------------------
# 4) Policy builder  (search + prompting)
# ---------------------------------------------------------------------


def prove_equality_interactive_policy(
    model_name: dp.StandardModelName,
    *,
    temperature: float | None = None,
    max_feedback_cycles: int = 3,
    cache_dir: str | Path | None = None,
) -> tuple[dp.SearchPolicy, dp.PromptingPolicy]:
    """
    Convenience factory that returns the `(search, prompting)` pair
    needed by `dp.run_strategy(...)`.

    • `max_feedback_cycles`  limits the # of Query ↔ Checker turns.
    • If `cache_dir` is given we wrap the LLM in an on‑disk cache.
    """
    # 1)  LLM  (with optional cache)
    llm = dp.standard_model(model_name)
    if cache_dir is not None:
        llm = dp.cached(llm, directory=Path(cache_dir))

    # 2)  Prompting policy  – one request per feedback cycle
    pp = dp.few_shot(llm, temperature=temperature, max_requests=1)

    # 3)  Search policy    –  retry loop around DFS
    #     • each cycle = two Branch layers   (ask + check)
    depth = 2 * (max_feedback_cycles + 1)
    sp = dp.loop() @ dfs(max_depth=depth)

    return (sp, pp)


# ---------------------------------------------------------------------
# 5) Quick helper for notebooks / REPL
# ---------------------------------------------------------------------


def ask_gpt_iteratively(model: str) -> dp.PromptingPolicy:
    """
    One‑liner to experiment outside the full strategy:

        pp     = ask_gpt_iteratively("gpt-4o")
        answer = dp.ask(ProveEqualityQuery(eq), pp)
    """
    return dp.few_shot(dp.openai_model(model), iterative_mode=True)
