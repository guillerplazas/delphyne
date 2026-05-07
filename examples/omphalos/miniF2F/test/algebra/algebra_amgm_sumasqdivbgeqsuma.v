(* miniF2F problem: algebra_amgm_sumasqdivbgeqsuma
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $a, b, c, d$ be positive real numbers. Show that $a^2 / b + b^2 / c + c^2 / d +
   d^2 / a \geq a + b + c + d$.

   Informal proof:
   Because $a, b, c, d$ are positive real numbers, so is $a+b+c+d$.
   Therefore it suffices to prove $(a^2 / b + b^2 / c + c^2 / d + d^2 / a)(a+b+c+d) \geq
   (a + b + c + d)^2$. By Cauchy-Schwarz, the left hand side has $(a^2 / b + b^2 / c +
   c^2 / d + d^2 / a)(a+b+c+d) \geq (\frac{a}{\sqrt{b}}*\sqrt{b} +
   \frac{b}{\sqrt{c}}*\sqrt{c} + \frac{c}{\sqrt{d}}*\sqrt{d} +
   \frac{d}{\sqrt{a}}*\sqrt{a})^2=RHS$. Hence the inequality holds.
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_amgm_sumasqdivbgeqsuma :
  forall a b c d : R,
  0 < a /\ 0 < b /\ 0 < c /\ 0 < d ->
  a^2 / b + b^2 / c + c^2 / d + d^2 / a >= a + b + c + d.
Proof.
Admitted.