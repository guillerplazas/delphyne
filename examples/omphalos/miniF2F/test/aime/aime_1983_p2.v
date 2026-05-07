(* miniF2F problem: aime_1983_p2
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f(x)=|x-p|+|x-15|+|x-p-15|$, where $0 < p < 15$. Determine the [[minimum]] value
   taken by $f(x)$ for $x$ in the [[interval]] $p \leq x\leq15$. Show that it is 015.

   Informal proof:
   It is best to get rid of the [[absolute value]]s first. 

   Under the given circumstances, we notice that $|x-p|=x-p$, $|x-15|=15-x$, and
   $|x-p-15|=15+p-x$.

   Adding these together, we find that the sum is equal to $30-x$, which attains its
   minimum value (on the given interval $p \leq x \leq 15$) when $x=15$, giving a
   minimum of $015$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem aime_1983_p2 :
  forall (x p : R) (f : R -> R),
  0 < p -> p < 15 ->
  p <= x -> x <= 15 ->
  f x = Rabs (x - p) + Rabs (x - 15) + Rabs (x - p - 15) ->
  15 <= f x.
Proof.
Admitted.