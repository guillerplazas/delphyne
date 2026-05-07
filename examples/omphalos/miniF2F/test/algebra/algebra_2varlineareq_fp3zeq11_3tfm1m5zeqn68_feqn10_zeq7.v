(* miniF2F problem: algebra_2varlineareq_fp3zeq11_3tfm1m5zeqn68_feqn10_zeq7
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given that $f + 3z = 11$ and $3(f - 1) - 5z = -68$, show that $f = -10$ and $z = 7$.

   Informal proof:
   We have that $-3 \times (f + 3z) = -3 \times 11$. Summing this with the second
   hypothesis, we get:
   $$(-3 \times (f + 3z)) + 3(f - 1) - 5z = -33 - 68$$
   So $-9z-3-5z=-101$, and $z = \frac{-101+3}{-14} = 7$.
   As a result, $f = 11 - 3z = 11 - 21 = -10$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem algebra_2varlineareq_fp3zeq11_3tfm1m5zeqn68_feqn10_zeq7:
  forall (f z : C),
  f + 3 * z = 11 ->
  3 * (f - 1) - 5 * z = -68 ->
  f = -10 /\ z = 7.

Proof.
Admitted.
