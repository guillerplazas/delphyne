# Luna xhigh and max diagnostic

User request: "Give me xhigh and max" following the Luna high result.
Twelve local trainX episodes: the same six saved states, seed 0, each at
xhigh and max. Original state order; xhigh/max on even rows and max/xhigh on
odd rows. Same fixed five-demo bank, gpt-5.6-luna, tools, Responses, output
limit 32768, temperature unset, four-request limit, verifier limits and
local $0.10 cap. New ceiling $1.20, allocated $0.60 per effort; no retry or
teacher budget, one worker. Previous unused allocations are not reused.

Primary endpoint is correct applicability versus archived Luna high.
Practical signal requires at least one additional correct decision without
losing an existing correct state. Report cost and cost/correct separately.
Five contrasts: medium versus each new effort, high versus each new effort,
and xhigh versus max. Family-clustered two-sided p<0.10, Holm over these
five contrasts per endpoint, descriptive 90% intervals. Practical and
statistical rules remain separate. Historical controls, one seed, six
inspected families and sequential user-requested exploration limit inference.
No global error control across previous campaigns is claimed.

Include failures and unsuccessful attempts in denominators; missing or
censored cells prevent ranking. Unknown is not a refutation. These episodes
stop after applicability, so correctness is not useful downstream progress
or a qualified full solve. Medium uses its saved applicability-phase costs,
excluding ordinary continuation. Full X caps remain $0.10. No full problems,
validation, new demonstrations or automatic expansion are included.

Implementation reuses the frozen strategy and ChangeConfig. A thin subclass
sets each worker's existing campaign-ledger stage to its actual effort,
keeping allocations separate. The inherited stage="terra" chooses the
applicability-only stop; model remains Luna. Local model plumbing forwards
xhigh/max directly. Configuration checks verify requested efforts, stages,
model and limits. Actual requests are audited after execution.

The executable docstring, registration, dependencies and archived controls
were frozen before paid calls. Both harnesses use the same supervised
launcher/tmux command in launch.json. No previous campaign is modified.
The savings-first deployment target remains >=15% lower full-problem total
cost and cost per qualified solve with no observed coverage loss. This
local effort diagnostic cannot establish that target or ACE value.
