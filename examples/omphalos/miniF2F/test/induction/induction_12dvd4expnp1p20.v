(* miniF2F problem: induction_12dvd4expnp1p20
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any natural number $n$, 12 divides $4^{n+1} + 20$.

   Informal proof:
   We have that $4 \equiv 4 \mod 12$ and $4^2 \equiv 4 \mod 12$. By immediate induction
   on $n$, we have that for every $n \geq 1$, $4^n \equiv 4 \mod 12$. As a result, for
   any natural number $n$, $4^{n+1} + 20 \equiv 4 + 20 \mod 12$. Since $12$ divides
   $24$, $12$ divides $4^{n+1} + 20$.
*)

Require Import Arith.

Theorem induction_12dvd4expnp1p20 :
  forall n : nat, exists k : nat, 4^(n+1) + 20 = 12 * k.

Proof.
Admitted.
