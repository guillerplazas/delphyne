(* miniF2F problem: mathd_numbertheory_221
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   How many natural numbers less than 1000 have exactly three distinct positive integer
   divisors? Show that it is 11.

   Informal proof:
   By the formula for the total number of positive divisors, only natural numbers in the
   form $p^{2}$ for some prime $p$ have exactly three positive divisors. Thus we must
   count the number of primes between 1 and $\sqrt{1000}$ (the squares of these primes
   are all the natural numbers less than 1000 that have exactly three positive
   divisors). There are $11$ such primes: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, and 31.
*)

Require Import Nat.
Require Import List.

Definition has_three_divisors (n : nat) : bool :=
  length (filter (fun d => n mod d =? 0) (seq 1 n)) =? 3.

Theorem mathd_numbertheory_221:
  length (filter has_three_divisors (seq 1 999)) = 11.
Proof.
Admitted.
