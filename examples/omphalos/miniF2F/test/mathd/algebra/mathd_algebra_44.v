(* miniF2F problem: mathd_algebra_44
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   At which point do the lines $s=9-2t$ and $t=3s+1$ intersect? Give your answer as an
   ordered pair in the form $(s, t).$ Show that it is (1,4).

   Informal proof:
   We can substitute the second equation into the first equation to get 
   $$s=9-2(3s+1)=9-6s-2.$$Moving the variable terms to the left-hand side and the
   constants to the right-hand side, we find $$s+6s=7.$$This gives  $s=1$ which we may
   plug into either equation to get $t$. For example, $$t=3(1)+1=4.$$So the lines
   intersect at the point $(1,4)$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_44:
  forall s t : R,
    (s = 9 - 2 * t) -> (t = 3 * s + 1) -> (s = 1 /\ t = 4).
Proof.
Admitted.