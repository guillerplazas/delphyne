(* miniF2F problem: mathd_numbertheory_136
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   When 39,500 is divided by an integer $n$, the quotient is 123 and the remainder is
   17. Find $n$. Show that it is 321.

   Informal proof:
   Turning our sentence into math we have \[39500=123n+17\]and we want to solve for $n$.
   That gives  \[n=\frac{39500-17}{123}=\frac{39483}{123}=321.\]
*)

Require Import Arith.

Theorem mathd_numbertheory_136 (n : nat) :
  123 * n + 17 = 39500 -> n = 321.
Proof.
Admitted.