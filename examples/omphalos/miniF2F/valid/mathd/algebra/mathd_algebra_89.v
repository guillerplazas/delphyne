(* miniF2F problem: mathd_algebra_89
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Simplify $(7b^3)^2 \cdot (4b^2)^{-3},$ given that $b$ is non-zero. Show that it is
   \frac{49}{64}.

   Informal proof:
   We see that $(7b^3)^2 = 7^2 \cdot b^{3\cdot2} = 49 \cdot b^6.$ Likewise, $(4b^2)^{-3}
   = 4^{-3} \cdot b^{-6}.$ Now, $(7b^3)^2 \cdot (4b^2)^{-3} = 49 \cdot b^6 \cdot 4^{-3}
   \cdot b^{-6},$ and since $4^{-3} = \frac{1}{64},$ we have $\frac{49}{64} \cdot b^6
   \cdot b^{-6} = \frac{49}{64},$ since $b^0 = 1$ for all non-zero $b.$
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_89:
  forall b : R,
  b <> 0 ->
  (7 * b^3)^2 * (1/((4 * b^2)^3)) = 49/64.
Proof.
Admitted.