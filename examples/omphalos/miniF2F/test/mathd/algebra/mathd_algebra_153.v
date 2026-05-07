(* miniF2F problem: mathd_algebra_153
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   We write $\lfloor X \rfloor$ to mean the greatest integer less than or equal to $X$;
   for example $\lfloor 3\frac{1}{2} \rfloor = 3$. If $N = \frac{1}{3}$, what is the
   value of $\lfloor 10N \rfloor + \lfloor 100N \rfloor + \lfloor 1000N \rfloor +
   \lfloor 10,000N \rfloor$? Show that it is 3702.

   Informal proof:
   Substituting, we get:

   $\lfloor 10N \rfloor$ = $\lfloor \frac {10}{3} \rfloor = 3$

   $\lfloor 100N \rfloor$ = $\lfloor \frac {100}{3} \rfloor = 33$

   $\lfloor 1000N \rfloor$ = $\lfloor \frac {1000}{3} \rfloor = 333$

   $\lfloor 10000N \rfloor$ = $\lfloor \frac {10000}{3} \rfloor = 3333$

   Adding these values, we get $3+33+333+3333 = 3702$
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_153 :
  forall n : R,
  n = 1/3 ->
  IZR (Int_part (10 * n)) + IZR (Int_part (100 * n)) + 
  IZR (Int_part (1000 * n)) + IZR (Int_part (10000 * n)) = 3702.

Proof.
Admitted.
