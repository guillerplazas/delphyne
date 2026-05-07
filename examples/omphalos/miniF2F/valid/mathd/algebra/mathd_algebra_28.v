(* miniF2F problem: mathd_algebra_28
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the largest number $c$ such that $2x^2+5x+c=0$ has at least one real
   solution? Express your answer as a common fraction. Show that it is \frac{25}{8}.

   Informal proof:
   In order for this quadratic to have at least one real solution, its discriminant must
   be non-negative. In other words, $b^2 - 4ac = 5^2 - 4(2)(c) = 25 - 8c \ge 0$.
   Rearranging, we have $25 \ge 8c$. Dividing by 8, we have $25/8 \ge c$. Therefore, the
   largest possible value of $c$ such that this quadratic has a real solution is
   $\frac{25}{8}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_28 :
  forall (c : R) (f : R -> R),
    (forall x, f x = 2 * x^2 + 5 * x + c) ->
    (exists x, f x <= 0) ->
    c <= 25 / 8.
Proof.
Admitted.