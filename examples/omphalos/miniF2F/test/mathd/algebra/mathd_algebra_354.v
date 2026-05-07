(* miniF2F problem: mathd_algebra_354
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   In an arithmetic sequence, the 7th term is 30, and the 11th term is 60. What is the
   21st term of this sequence? Show that it is 135.

   Informal proof:
   Let $a$ be the first term in this arithmetic sequence, and let $d$ be the common
   difference.  Then the $7^{\text{th}}$ term is $a + 6d = 30$, and the $11^{\text{th}}$
   term is $a + 10d = 60$.  Subtracting these equations, we get $4d = 30$, so $d = 30/4
   = 15/2$.

   Then the $21^{\text{st}}$ term is $a + 20d = (a + 10d) + 10d = 60 + 10 \cdot 15/2 =
   135$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_354 :
  forall a d : R,
    (a + 6 * d = 30) ->
    (a + 10 * d = 60) ->
    (a + 20 * d = 135).
Proof.
Admitted.