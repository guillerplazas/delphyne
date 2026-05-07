(* miniF2F problem: mathd_algebra_616
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given the two functions $f(x)=x^3+2x+1$ and $g(x)=x-1$, find $f(g(1))$. Show that it
   is 1.

   Informal proof:
   Since we know that $f(x)=x^3+2x+1$ and $g(x)=x-1$, we can express $f(g(1))$ as
   $(x-1)^3+2(x-1)+1$. Thus, when $x=1$ we find \begin{align*}
   (f(g(1))&=(1-1)^3+2(1-1)+1
   \\ &=(0)^3+2(0)+1
   \\ &=0+0+1
   \\&=1
   \end{align*}
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_616
  (f g : R -> R)
  (h₀ : forall x, f x = x^3 + 2 * x + 1)
  (h₁ : forall x, g x = x - 1) :
  f (g 1) = 1.
Proof.
Admitted.