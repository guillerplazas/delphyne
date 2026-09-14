# Rocq-checked snippets for ACE

`CheckRocqSnippet` lets the flagship grounded prover and ACE writing roles
check unfamiliar syntax and names in Rocq before using them. This is an
opt-in strategy tool shared by Codex and Claude Code; it uses Delphyne
Compute and the normal bounded socket bridge. It does not use rocq-mcp.

The caller supplies a `context_id` from the query's catalogue and exact raw
Rocq sentences. The context binds the theorem file hash, imports and verified
prefix. Rocq executes the complete snippet, including any malformed trailing
text. A successful fragment receives a receipt and a successor context.

| Verdict | Meaning |
| --- | --- |
| `rejected` | Rocq rejected the exact input, or the input was empty/unsafe/fenced. |
| `executed_open` | The snippet executed in that source context; proof obligations remain. |
| `completed` | Rocq also accepted Qed. The prover immediately returns this proof. |
| `resource_exhausted` | The bounded check could not establish a verdict. |
| `unknown` | Evidence was unavailable, such as a transport failure. |

These receipts establish source-local validity. They do not certify that a
snippet will work with different names or hypotheses, or that a valid fragment
is useful. Adapted snippets require another check. The prover keeps its usual
full-proof submission path and has at most four tool interactions, within its
existing money, request and Rocq allowances. Duplicate probes reuse receipts
while consuming the interaction allowance.

Enable `snippet_tools=True` on `prove_theorem_grounded`. The versioned query
classes then advertise the tool; the default remains false. `snippet_policy`
in `prove_snippets.py` composes the existing grounded search, few-shot policy,
budget observer, recorded transport and campaign model. Register
`demos/snippets.demo.yaml` in the execution context for its two train-only
examples. `snippet_examples()` excludes the source theorem family. Each
demonstration closes all tool conversations and has a Rocq-checked final proof.

`write_checked_rocq_advice` exposes the same checker to reflector, curator and
reducer. Four model turns permit at most three probes, followed by a final
answer without tools. Curator/reducer additions contain plain explanation and
receipt IDs. The strategy renders executable code from those receipts;
every available checked receipt must be retained or explicitly dropped.
Plain prose is not certified. Tool availability alone does not force use.

Run the free regression suite from `examples/omphalos` in either harness:

```sh
python -m pytest -q tests/test_snippet_tool.py tests/test_terminal_evidence.py
```

The executable demonstrations can be rebuilt with
`python -m tools.data.snippet_demos`. This invokes local Rocq, with no API
request. Rebuilding changes demonstration receipts, so it must precede a
campaign seal. `python -m tools.reports.snippet_checks` performs the six-case
socket/legacy-stdio semantic parity check; bounded stdio remains unsupported.

For experiments, install `runtime.snippet_scope.install()` before imports.
Use the registered entry point `experiments.snippet_experiment`; it requires
the existing campaign ledger, reservations and source seal. Long runs source
`~/.config/omphalos/env.sh` inside their tmux session. A credential precheck
prevents worker dispatch when that environment is absent. Normal campaign
execution and reporting are documented in
`experiments/campaigns/ace_snippets_20260913/README.md`.

Comparison outcomes and limitations are in that campaign's `FINDINGS.md`.
No default or frozen book is changed automatically. TestX and protected
challenge evidence remain closed.
