(* miniF2F problem: mathd_algebra_196
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the sum of all solutions of the equation $|2-x|= 3$. Show that it is 4.

   Informal proof:
   In order to have $|2-x| = 3$, we must have $2-x = 3$ or $2-x = -3$.  If $2-x = 3$,
   then $x=-1$, and if $2-x = -3$, then $x = 5$.  The sum of these solutions is $(-1) +
   5 = 4$.
*)

Require Import Reals.
Require Import ClassicalDescription.

Open Scope R_scope.

Theorem mathd_algebra_196 :
  exists (S : R -> Prop),
  (forall x, S x <-> Rabs (2 - x) = 3) /\
  exists sumS, 
    (forall x, S x -> x = -1 \/ x = 5) /\
    (S (-1) /\ S 5) /\
    sumS = -1 + 5 /\
    sumS = 4.

Proof.
Admitted.
