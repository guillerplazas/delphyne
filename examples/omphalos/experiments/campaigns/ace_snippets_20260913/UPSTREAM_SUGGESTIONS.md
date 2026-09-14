# Useful upstream changes (not implemented)

The Responses translator checks the order of tool outputs but does not reject
an unanswered trailing function call before sending a request. The snippet
demonstration integration exposed both failures: two examples failed locally
on ordering; one example reached a provider HTTP 400 for a missing output.
Add an explicit end-of-chat pending-call check in Delphyne's translator and a
command/demo validation check that covers the full rendered few-shot request.
Omphalos now tests all 60 permitted problem prompts locally without changing
the upstream translator.

RunStrategy's in-memory result values may contain tuples, while saved YAML
uses lists. A framework helper for comparing canonical serialized command
outcomes would avoid duplicating this conversion in experiment replay tools.
The Omphalos replay check now normalizes only the value representation; exact
transport state, success, budget and cached request checks remain intact.

All implemented code remains inside `examples/omphalos`.
