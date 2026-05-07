(* miniF2F problem: mathd_algebra_59
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $F(a, b, c, d) = a^b + c ^ d$, what is the value of $b$ such that $F(4, b, 2, 3) =
   12$? Show that it is 1.

   Informal proof:
   Plugging in, we have that $4^b + 2^3 = 12$.  This rearranges to $4^b = 4$, or $b =
   1$.
*)

Require Import Reals Rpower.

Open Scope R_scope.



Theorem mathd_algebra_59 :
  forall b : R,
    Rpower 4 b + Rpower 2 3 = 12 ->
    b = 1.

Proof.
Admitted.
