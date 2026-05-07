(* miniF2F problem: aime_1988_p8
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The function $f$, defined on the set of ordered pairs of positive integers, satisfies
   the following properties:
   $ f(x, x) = x,\; f(x, y) = f(y, x), {\rm \ and\ } (x+y)f(x, y) = yf(x, x+y). $
   Calculate $f(14,52)$. Show that it is 364.

   Informal proof:
   Let $z = x+y$. By the substitution $z=x+y,$ we rewrite the third property in terms of
   $x$ and $z,$ then solve for $f(x,z):$
   $\begin{align*}
   zf(x,z-x) &= (z-x)f(x,z) \\
   f(x,z) &= \frac{z}{z-x} \cdot f(x,z-x).
   \end{align*}$
   Using the properties of $f,$ we have
   $\begin{align*}
   f(14,52) &= \frac{52}{38} \cdot f(14,38) \\
   &= \frac{52}{38} \cdot \frac{38}{24} \cdot f(14,24) \\
   &= \frac{52}{38} \cdot \frac{38}{24} \cdot \frac{24}{10} \cdot f(14,10)\\
   &= \frac{52}{38} \cdot \frac{38}{24} \cdot \frac{24}{10} \cdot f(10,14)\\
   &= \frac{52}{38} \cdot \frac{38}{24} \cdot \frac{24}{10} \cdot \frac{14}{4} \cdot
   f(10,4)\\
   &= \frac{52}{38} \cdot \frac{38}{24} \cdot \frac{24}{10} \cdot \frac{14}{4} \cdot
   f(4,10)\\
   &= \frac{52}{38} \cdot \frac{38}{24} \cdot \frac{24}{10} \cdot \frac{14}{4} \cdot
   \frac{10}{6} \cdot f(4,6)\\
   &= \frac{52}{38} \cdot \frac{38}{24} \cdot \frac{24}{10} \cdot \frac{14}{4} \cdot
   \frac{10}{6} \cdot \frac{6}{2} \cdot f(4,2)\\
   &= \frac{52}{38} \cdot \frac{38}{24} \cdot \frac{24}{10} \cdot \frac{14}{4} \cdot
   \frac{10}{6} \cdot \frac{6}{2} \cdot f(2,4)\\
   &= \frac{52}{38} \cdot \frac{38}{24} \cdot \frac{24}{10} \cdot \frac{14}{4} \cdot
   \frac{10}{6} \cdot \frac{6}{2} \cdot \frac{4}{2} \cdot f(2,2)\\
   &= \frac{52}{38} \cdot \frac{38}{24} \cdot \frac{24}{10} \cdot \frac{14}{4} \cdot
   \frac{10}{6} \cdot \frac{6}{2} \cdot \frac{4}{2} \cdot 2\\
   &=364.
   \end{align*}$
   ~MRENTHUSIASM (credit given to AoPS)
*)

Require Import Reals.

Open Scope R_scope.

Theorem aime_1988_p8 :
  forall f : nat -> nat -> R,
  (forall x, (x > 0)%nat -> f x x = INR x) ->
  (forall x y, (x > 0)%nat -> (y > 0)%nat -> f x y = f y x) ->
  (forall x y, (x > 0)%nat -> (y > 0)%nat ->
      (INR x + INR y) * f x y = INR y * f x (x + y)%nat) ->
  f 14%nat 52%nat = 364.
Proof.
Admitted.
