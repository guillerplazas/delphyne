(* miniF2F problem: mathd_numbertheory_780
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose $m$ is a two-digit positive integer such that $6^{-1}\pmod m$ exists and
   $6^{-1}\equiv 6^2\pmod m$. What is $m$? Show that it is 43.

   Informal proof:
   We can multiply both sides of the congruence $6^{-1}\equiv 6^2\pmod m$ by $6$: $$
   \underbrace{6\cdot 6^{-1}}_1 \equiv \underbrace{6\cdot 6^2}_{6^3} \pmod m.
   $$Thus $6^3-1=215$ is a multiple of $m$. We know that $m$ has two digits. The only
   two-digit positive divisor of $215$ is $43$, so $m=43$.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem mathd_numbertheory_780 :
  forall m x : Z,
    10 <= m ->
    m <= 99 ->
    (6 * x) mod m = 1 ->
    (x - 36) mod m = 0 ->
    m = 43.
Proof.
Admitted.