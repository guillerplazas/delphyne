(* miniF2F problem: mathd_numbertheory_42
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the sum of the smallest and second-smallest positive integers $a$ satisfying
   the congruence $$27a\equiv 17 \pmod{40}~?$$ Show that it is 62.

   Informal proof:
   Note that $27$ and $40$ are relatively prime, so $27$ has an inverse $\pmod{40}$.
   Conveniently, the inverse of $27\pmod{40}$ is easily found to be $3$, as we have
   $27\cdot 3 = 81\equiv 1\pmod{40}$.

   To solve the congruence $27a\equiv 17\pmod{40}$, we multiply both sides by $3$ and
   simplify: \begin{align*}
   3\cdot 27a &\equiv 3\cdot 17 \pmod{40} \\
   a &\equiv 51 \pmod{40} \\
   a &\equiv 11 \pmod{40}
   \end{align*}Each operation in this sequence is reversible, so the solution set is
   exactly the set of integers congruent to $11\pmod{40}$. The smallest and
   second-smallest positive solutions are $11$ and $51$. Their sum is $62$.
*)

Require Import PeanoNat.
Require Import Arith.

Theorem mathd_numbertheory_42 :
  forall u v : nat,
  (27 * u mod 40 = 17) ->
  (27 * v mod 40 = 17) ->
  (u < 40) ->
  (v < 80) ->
  (40 < v) ->
  (u + v = 62).
Proof.
Admitted.