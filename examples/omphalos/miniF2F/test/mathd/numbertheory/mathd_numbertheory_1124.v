(* miniF2F problem: mathd_numbertheory_1124
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The four-digit number $\underline{374n}$ is divisible by 18. Find the units digit
   $n$. Show that it is 4.

   Informal proof:
   We know that the prime factorization of 18 is $2\cdot 3^2$, so in order for the four
   digit number to be divisible by 18 it must also be divisible by 9 and 2. In order for
   a number to be divisible by 9, the sum of its digits must be divisible by 9 as well.
   Thus, $3+7+4+n$, or $14+n$, must be divisible by 9. Since 18 is the smallest multiple
   of 9 that is greater than 10, $14+n=18$, and $n=18-14=4$.
*)

Require Import Nat.
Require Import ZArith.

Theorem mathd_numbertheory_1124 :
  forall n : nat,
  n <= 9 ->
  (exists k : nat, 374 * 10 + n = 18 * k) ->
  n = 4.

Proof.
Admitted.
