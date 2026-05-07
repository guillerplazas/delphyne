(* miniF2F problem: mathd_algebra_148
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given $f(x)=cx^3-9x+3$ and $f(2)=9$, find the value of $c$. Show that it is 3.

   Informal proof:
   Plugging $x=2$ into the expression for $f(x)$, we find
   $f(2)=c(2^3)-9(2)+3=8c-18+3=8c-15$. Since we know that $f(2)=9$, \begin{align*}
   f(2)&= 9
   \\\Rightarrow\qquad8c-15&=9
   \\\Rightarrow\qquad8c&=24
   \\\Rightarrow\qquad c&=3
   \end{align*}
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_148 :
  forall (c : R) (f : R -> R),
  (forall x, f x = c * x^3 - 9 * x + 3) ->
  f 2 = 9 ->
  c = 3.
Proof.
Admitted.