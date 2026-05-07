(* miniF2F problem: mathd_numbertheory_458
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   When all the girls at Madeline's school line up in rows of eight, there are seven
   left over.

   If instead they line up in rows of four, how many are left over? Show that it is 3.

   Informal proof:
   The number of girls is of the form $8n+7$, where $n$ is some integer (the number of
   rows). This expression can also be written as $4(2n+1)+3$, so when the girls line up
   in rows of four, they make $2n+1$ rows with $3$ girls left over.
*)

Require Import Arith.

Theorem mathd_numbertheory_458:
  forall n : nat,
  n mod 8 = 7 -> n mod 4 = 3.
Proof.
Admitted.