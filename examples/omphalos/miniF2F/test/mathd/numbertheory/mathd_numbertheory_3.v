(* miniF2F problem: mathd_numbertheory_3
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the units digit of the sum of the squares of the first nine positive
   integers? Show that it is 5.

   Informal proof:
   We can reduce the amount of work we have to do in this problem by realizing that the
   units digit of the sum of the squares is the units digit of the sum of the units
   digits of the squares. In other words, the units digit of $1^2+2^2+\ldots+9^2$ is the
   units digit of $1+4+9+6+5+6+9+4+1=45$, which is $5$.
*)

Require Import Coq.Arith.Arith.



Theorem mathd_numbertheory_3 :
  ((1 * 1) +
   (2 * 2) +
   (3 * 3) +
   (4 * 4) +
   (5 * 5) +
   (6 * 6) +
   (7 * 7) +
   (8 * 8) +
   (9 * 9)) mod 10 = 5.

Proof.
Admitted.
