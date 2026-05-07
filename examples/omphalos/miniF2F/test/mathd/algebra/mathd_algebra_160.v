(* miniF2F problem: mathd_algebra_160
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For each plumbing repair job, Mr. Wrench charges $N$ dollars for coming out to the
   house plus $x$ dollars per hour that he works at the house. He charged $\$97$ for a
   one-hour repair job and $\$265$ for a five-hour repair job. What is his charge for a
   two-hour repair job? Show that it is \$ 139.

   Informal proof:
   We can rewrite the problem as the system of equations: \begin{align*}
   N+x &= 97\\
   N+5x &= 265
   \end{align*}Subtracting these gives: \begin{align*}
   4x &= 265-97=168\\
   x &= 42.
   \end{align*}So now $N = 97-42= 55$. So the charge for a two-hour repair job is $N+2x
   = \$ 55+2\cdot \$ 42 = \$ 139$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_160 (n x : R) :
  (n + x = 97) ->
  (n + 5 * x = 265) ->
  (n + 2 * x = 139).
Proof.
Admitted.