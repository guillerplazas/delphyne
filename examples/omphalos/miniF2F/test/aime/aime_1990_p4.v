(* miniF2F problem: aime_1990_p4
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the positive solution to
   <center>$\frac 1{x^2-10x-29}+\frac1{x^2-10x-45}-\frac 2{x^2-10x-69}=0$</center> Show
   that it is 013.

   Informal proof:
   We could clear out the denominators by multiplying, though that would be
   unnecessarily tedious.

   To simplify the equation, substitute $a = x^2 - 10x - 29$ (the denominator of the
   first fraction). We can rewrite the equation as $\frac{1}{a} + \frac{1}{a - 16} -
   \frac{2}{a - 40} = 0$. Multiplying out the denominators now, we get:

   $(a - 16)(a - 40) + a(a - 40) - 2(a)(a - 16) = 0$

   Simplifying, $-64a + 40 \times 16 = 0$, so $a = 10$. Re-substituting, $10 = x^2 - 10x
   - 29 \Longleftrightarrow 0 = (x - 13)(x + 3)$. The positive [[root]] is $013$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem aime_1990_p4:
  forall x : R,
  0 < x ->
  x^2 - 10*x - 29 <> 0 ->
  x^2 - 10*x - 45 <> 0 ->
  x^2 - 10*x - 69 <> 0 ->
  1/(x^2 - 10*x - 29) + 1/(x^2 - 10*x - 45) - 2/(x^2 - 10*x - 69) = 0 ->
  x = 13.
Proof.
Admitted.