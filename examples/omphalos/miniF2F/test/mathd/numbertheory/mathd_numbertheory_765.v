(* miniF2F problem: mathd_numbertheory_765
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the largest negative integer $x$ satisfying $$24x \equiv 15 \pmod{1199}~?$$
   Show that it is -449.

   Informal proof:
   To start, notice that $24\cdot 50 = 1200\equiv 1\pmod{1199}$ (in other words, $24$
   and $50$ are inverses modulo $1199$).

   To solve the congruence $24x\equiv 15\pmod{1199}$, we multiply both sides by $50$ and
   simplify: \begin{align*}
   50\cdot 24x &\equiv 50\cdot 15 \pmod{1199} \\
   x &\equiv 750 \pmod{1199}
   \end{align*}This process can also be reversed (by multiplying both sides by
   $50^{-1}=24$), so the solutions to the original congruence are precisely the same as
   the solutions to $x\equiv 750\pmod{1199}$. The largest negative solution is $750-1199
   = -449$.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem mathd_numbertheory_765:
  forall x : Z,
    x < 0 ->
    (24 * x mod 1199 = 15) ->
    x <= -449.
Proof.
Admitted.