(* miniF2F problem: mathd_algebra_77
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose that $a$ and $b$ are nonzero real numbers, and that the equation  $${x^2 + ax
   + b = 0}$$ has solutions $a$ and $b$. Then what is the pair $(a,b)$? Show that it is
   (1,-2).

   Informal proof:
   The given conditions imply that $$
   x^2 + ax + b = (x-a)(x-b) = x^2 -(a+b)x + ab,
   $$ so $$
   a+b = -a \quad\text{and}\quad ab = b.
   $$ Since $b \neq 0$, the second equation implies that $a=1$. The first equation gives
   $b=-2$, so $(a,b) = (1,-2)$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_77 :
  forall a b : R,
  a <> 0 -> b <> 0 -> a <> b ->
  (forall x, (fun x => x^2 + a*x + b) x = x^2 + a*x + b) ->
  (fun x => x^2 + a*x + b) a = 0 ->
  (fun x => x^2 + a*x + b) b = 0 ->
  a = 1 /\ b = -2.
Proof.
Admitted.