(* miniF2F problem: mathd_algebra_142
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   A line $\ell$ passes through the points $B(7,-1)$ and $C(-1,7)$.  The equation of
   this line can be written in the form $y=mx+b$; compute $m+b$. Show that it is 5.

   Informal proof:
   The line through points $B$ and $C$ has slope $\dfrac{-1-7}{7-(-1)}=-1$.  Since
   $(7,-1)$ lies on the line, the line has equation $$y-(-1)=-1(x-7),$$or $y = -x + 6$. 
   Thus $m=-1$, $b=6$, and $m+b=-1+6=5$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_142 :
  forall (m b : R), 
  (m * 7 + b = -1) -> 
  (m * (-1) + b = 7) -> 
  (m + b = 5).
Proof.
Admitted.