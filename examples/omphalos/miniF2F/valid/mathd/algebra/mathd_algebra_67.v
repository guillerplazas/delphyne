(* miniF2F problem: mathd_algebra_67
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f(x) = 5x+3$ and $g(x)=x^2-2$. What is $g(f(-1))$? Show that it is 2.

   Informal proof:
   We note that $f(-1)=5\cdot(-1)+3=-2$, so substituting that in we get
   $g(f(-1))=g(-2)=(-2)^2-2=2$. Therefore our answer is $2$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_67 
  (f g : R -> R)
  (h0 : forall x, f x = 5 * x + 3)
  (h1 : forall x, g x = x^2 - 2) :
  g (f (-1)) = 2.
Proof.
Admitted.