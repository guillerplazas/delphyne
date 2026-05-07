(* miniF2F problem: algebra_2varlineareq_xpeeq7_2xpeeq3_eeq11_xeqn4
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given two complex numbers x and e, if we assume that $x + e = 7$ and $2x + e = 3$,
   then show that $e = 11$ and $x=-4$.

   Informal proof:
   First, $x = 2x + e - (x + e) = 3 - 7 = -4$. Then, substituting $x=-4$ in $x+e=7$, we
   obtain $e=11$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem algebra_2varlineareq_xpeeq7_2xpeeq3_eeq11_xeqn4
  (x e : C)
  (h0 : x + e = 7)
  (h1 : 2 * x + e = 3) :
  e = 11 /\ x = -4.

Proof.
Admitted.
