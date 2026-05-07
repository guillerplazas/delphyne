(* miniF2F problem: mathd_algebra_513
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $3a+2b=5$ and $a+b=2$, what is the ordered pair $(a,b)$ that satisfies both
   equations? Show that it is (1,1).

   Informal proof:
   We wish to solve for $a$ and $b$. First, multiply the second equation by $2$ and
   subtract it from the first. This gives $(3a - 2a) + (2b - 2b) = (5 - 4)$, or $a = 1$.
   Then, plugging $a = 1$ into the second equation yields $1 + b = 2$, so $b = 1$. Thus,
   the ordered pair $(a,b)$ that satisfies both equations is $(1,1)$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_513 :
  forall (a b : R),
  (3 * a + 2 * b = 5) -> 
  (a + b = 2) -> 
  (a = 1 /\ b = 1).
Proof.
Admitted.