(* miniF2F problem: mathd_numbertheory_110
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   In this problem, $a$ and $b$ are integers, such that $a \ge b.$

   If $a+b\equiv 2\pmod{10}$ and $2a+b\equiv 1\pmod{10}$, then what is the last digit of
   $a-b$? Show that it is 6.

   Informal proof:
   To determine the residue of $a\pmod{10}$, we can subtract $a+b$ from $2a+b$:
   \begin{align*}
   a &= (2a+b) - (a+b) \\
   &\equiv 1 - 2 \\
   &\equiv -1 \\
   &\equiv 9 \pmod{10}.
   \end{align*}Then we know that $9+b\equiv 2\pmod{10}$, so we can solve for $b$:
   \begin{align*}
   b &\equiv 2-9 \\
   &\equiv -7 \\
   &\equiv 3 \pmod{10}.
   \end{align*}Finally, we substitute to obtain $$a-b \equiv 9-3 \equiv 6
   \pmod{10},$$and so the last digit of $a-b$ is $6$.
*)

Require Import Arith.
Require Import ZArith.

Theorem mathd_numbertheory_110:
  forall a b : nat,
  (0 < a)%nat -> (0 < b)%nat -> (b <= a)%nat ->
  (a + b) mod 10 = 2 ->
  (2 * a + b) mod 10 = 1 ->
  (a - b) mod 10 = 6.
Proof.
Admitted.