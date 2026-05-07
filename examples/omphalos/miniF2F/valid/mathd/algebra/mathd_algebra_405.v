(* miniF2F problem: mathd_algebra_405
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For how many positive integer values of $x$ is the sum $x^2+4x+4$ less than 20? Show
   that it is 2.

   Informal proof:
   Note that since we can only use positive integers for $x$, the minimum will be x = 1.
   Testing x = 2, we get $2^2 + 4\cdot 2 + 4 = 16$.  Since $3^2 - 2^2 = 5$, we know that
   only $x = 1,2$ will work, thus, there are $2$ positive integer values of $x$ such
   that this function is less than 20.
*)

Require Import Arith.

Theorem mathd_algebra_405 :
  forall x : nat, 0 < x -> x^2 + 4 * x + 4 < 20 -> (x = 1 \/ x = 2).
Proof.
Admitted.