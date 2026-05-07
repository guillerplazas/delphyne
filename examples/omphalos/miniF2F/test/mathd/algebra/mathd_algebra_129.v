(* miniF2F problem: mathd_algebra_129
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Solve for $a$: $\dfrac{8^{-1}}{4^{-1}}-a^{-1}=1$. Show that it is -2.

   Informal proof:
   First, we simplify the left side, using the exponent rule $x^{-1} = \frac1x$.  We
   have  \[
   \frac{8^{-1}}{4^{-1}} - a^{-1} = \frac{1/8}{1/4} - \frac1a = \frac18\cdot \frac41
   -\frac{1}{a}= \frac{1}{2} - \frac1a,
   \] so we can write the original equation as $\frac12 - \frac1a = 1$.  Subtracting
   $\frac12$ from both sides gives $-\frac1a = \frac12$, and taking the reciprocal of
   both sides gives $-a = 2$.  Therefore, we have $a = -2$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_129:
  forall a : R,
  a <> 0 ->
  (/ 8) / (/ 4) - / a = 1 ->
  a = -2.
Proof.
Admitted.