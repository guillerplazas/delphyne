(* miniF2F problem: mathd_numbertheory_541
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The product of two positive whole numbers is 2005. If neither number is 1, what is
   the sum of the two numbers? Show that it is 406.

   Informal proof:
   $2005=5\cdot401$. Checking the primes less than $\sqrt{401}$ as potential divisors,
   we see that 401 is prime. Thus, the positive whole numbers in question are 5 and 401.
   Their sum is $406.$
*)

Require Import Arith.

Theorem mathd_numbertheory_541 :
  forall (m n : nat),
  1 < m ->
  1 < n ->
  m * n = 2005 ->
  m + n = 406.
Proof.
Admitted.