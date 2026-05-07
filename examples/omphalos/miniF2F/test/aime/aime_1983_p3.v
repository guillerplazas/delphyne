(* miniF2F problem: aime_1983_p3
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the product of the [[real]] [[root]]s of the [[equation]] $x^2 + 18x + 30 = 2
   \sqrt{x^2 + 18x + 45}$? Show that it is 020.

   Informal proof:
   If we were to expand by squaring, we would get a [[quartic Equation|quartic]]
   [[polynomial]], which isn't always the easiest thing to deal with.

   Instead, we substitute $y$ for $x^2+18x+30$, so that the equation becomes
   $y=2\sqrt{y+15}$.

   Now we can square; solving for $y$, we get $y=10$ or $y=-6$. The second root is
   extraneous since $2\sqrt{y+15}$ is always non-negative (and moreover, plugging in
   $y=-6$, we get $-6=6$, which is obviously false). Hence we have $y=10$ as the only
   solution for $y$. Substituting $x^2+18x+30$ back in for $y$,

   <center>$x^2+18x+30=10 \Longrightarrow x^2+18x+20=0.$</center> Both of the roots of
   this equation are real, since its discriminant is $18^2 - 4 \cdot 1 \cdot 20 = 244$,
   which is positive. Thus by [[Vieta's formulas]], the product of the real roots is
   simply $020$.
*)

Require Import Reals.
Require Import List.
Require Import SetoidList.
Open Scope R_scope.

Theorem aime_1983_p3 :
  forall (f : R -> R)
         (roots : list R),
  (forall x, f x = x^2 + 18*x + 30 - 2 * sqrt(x^2 + 18*x + 45)) ->
  (forall x, In x roots <-> f x = 0) ->
  NoDup roots ->
  fold_left Rmult roots 1 = 20.

Proof.
Admitted.
