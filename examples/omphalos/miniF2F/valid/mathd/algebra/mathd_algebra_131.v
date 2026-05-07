(* miniF2F problem: mathd_algebra_131
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find $\frac{1}{a-1}+\frac{1}{b-1},$ where $a$ and $b$ are the roots of the quadratic
   equation $2x^2-7x+2 = 0.$ Show that it is -1.

   Informal proof:
   We use the fact that the sum and product of the roots of a quadratic equation
   $ax^2+bx+c = 0$ are given by $-b/a$ and $c/a,$ respectively. This means that $a+b =
   7/2$ and $ab = 2/2 = 1.$ Now we manipulate the expression
   $\frac{1}{a-1}+\frac{1}{b-1}$ to get:  $$\frac{1}{a-1}+\frac{1}{b-1} =
   \frac{b-1}{(a-1)(b-1)} + \frac{a-1}{(a-1)(b-1)} = \frac{(a+b)-2}{(a-1)(b-1)}.$$ But
   the denominator $$(a-1)(b-1) = ab - a - b + 1 = (ab) - (a+b) + 1 = 1 - 7/2 + 1 = 2 -
   7/2,$$ whereas the numerator $a+b-2 = 7/2 - 2.$

   Thus, our answer is $\frac{7/2-2}{2-7/2} = -1.$
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_131 :
  forall (a b : R) (f : R -> R),
    (forall x, f x = 2 * x^2 - 7 * x + 2) ->
    f a = 0 ->
    f b = 0 ->
    a <> b ->
    1 / (a - 1) + 1 / (b - 1) = -1.
Proof.
Admitted.