# Prepared file excerpts

Read-only excerpts for rehearsal; no model or Rocq calls.

## prove_ace.py:92

```python
class ProposeProofScriptACE(ProposeProofScriptAgentic):
    """
    The agentic proposal query, plus a playbook.

    A separate query class rather than a new field on the agentic one:
    `query_name()` derives template names and cache identities from
    the class name, so the frozen `ProposeProofScriptAgentic` prompts
    and caches cannot be perturbed by anything this class does. The
    ACE templates `{% include %}` the agentic ones and append a
    playbook section (see `prompts/ace/generation/ProposeProofScriptACE.system.jinja`).

    `playbook` is the *rendered* playbook (`Playbook.render_markdown`
    for v1, `Playbook.render_prompt` for v2), not a file path: the
    query must be self-contained so that cached runs replay without
    reading external state. Empty string = no playbook section, which
    makes the prompt byte-identical to the agentic baseline's (v2's
    empty rendering; v1 rendered a placeholder line instead).
    """

    playbook: str = ""
    render_version: int = 1
```

## prove_ace.py:289

```python
class ReflectOnTrajectory(dp.Query[Reflection]):
    """
    One-shot Reflector query.

    Inputs are plain strings so the query is self-contained (cache
    keys must not depend on external files): `outcome` is the verdict
    line ("SOLVED ..." / "NOT SOLVED ..."), `playbook` the rendered
    markdown with bullet ids, `trajectory` the rendered transcript of
    the attempt (see `experiments/ace/ace_adaptation.py` for the exact
    rendering). There are no ground-truth labels in this domain; the
    Rocq verifier's feedback inside the trajectory is the only
    supervision (the paper's "offline, no GT labels" setting).
    """

    spec: pt.ProblemSpec
    outcome: str
    playbook: str
    trajectory: str

    __parser__ = dp.last_code_block.yaml

```

## runtime/campaign_budget.py:262

```python
    def _input_bound(self, req: LLMRequest) -> int:
        inp, _ = oa.translate_chat_for_responses(
            req, self.reasoning_cache, self.convert_user_feedback_to_tool
        )
        tools = [oa._make_responses_tool(t) for t in req.tools]  # pyright: ignore[reportPrivateUsage]
        fmt = oa._responses_response_format(  # pyright: ignore[reportPrivateUsage]
            req.structured_output, self.no_json_schema
        )
        return (
            len(json.dumps([inp, tools, fmt], default=str).encode())
            + self.reasoning_allowance
            + 32768
        )

    @override
    def estimate_budget(self, req: LLMRequest) -> Budget:
        estimate = super().estimate_budget(req)
        if not self.estimate_dollars:
            return estimate
        full = self.add_model_defaults(req)
        assert self.pricing is not None
        bound = (
            self._input_bound(full) * self.pricing.dollars_per_input_token
            + full.options.get("max_completion_tokens", self.output_limit)
            * self.pricing.dollars_per_output_token
        )
        return estimate + Budget({"price": bound})

    @override
```

## Terminal witness: first array entry

```json
{
  "theorem": "amc12_2000_p6",
  "final_tactic_visible": false,
  "last_tactic": "nia.",
  "final_check.category": "accepted",
  "final_check.success": true,
  "verified_code_last_line": "nia."
}
```

The `false` flag means the accepted terminal tactic was missing from the last submitted text. It is not a failed proof.
