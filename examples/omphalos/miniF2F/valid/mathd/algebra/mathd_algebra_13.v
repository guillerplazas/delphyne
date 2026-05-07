(* miniF2F problem: mathd_algebra_13
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find $A$ and $B$ such that
   \[\frac{4x}{x^2-8x+15} = \frac{A}{x-3} + \frac{B}{x-5}\]for all $x$ besides 3 and 5.
   Express your answer as an ordered pair in the form $(A, B).$ Show that it is (-6,
   10).

   Informal proof:
   Factoring the denominator on the left side gives \[
   \frac{4x}{(x-5)(x-3)}=\frac{A}{x-3}+\frac{B}{x-5}. \]Then, we multiply both sides of
   the equation by $(x - 3)(x - 5)$ to get \[ 4x = A(x-5) + B(x-3). \]If the linear
   expression $4x$ agrees with the linear expression $A(x-5) + B(x-3)$ at all values of
   $x$ besides 3 and 5, then the two expressions must agree for $x=3$ and $x=5$ as well.
   Substituting $x = 3$, we get $12 = -2A$, so $A = -6$.  Likewise, we plug in $x = 5$
   to solve for $B$. Substituting $x = 5$, we get $20 = 2B$, so $B = 10$.  Therefore,
   $(A, B) = (-6, 10).$
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_13:
  forall (A B : R),
  (forall x : R, (x - 3 <> 0) /\ (x - 5 <> 0) -> 
    4 * x / (x ^ 2 - 8 * x + 15) = A / (x - 3) + B / (x - 5)) ->
  A = -6 /\ B = 10.
Proof.
Admitted.