(* miniF2F problem: mathd_algebra_158
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The sum of 5 consecutive even integers is 4 less than the sum of the first 8
   consecutive odd counting numbers. What is the smallest of the even integers? Show
   that it is 8.

   Informal proof:
   The first 8 odd positive integers are 1, 3, $\dots$, 15.  The sum of an arithmetic
   series is equal to the average of the first and last term, multiplied by the number
   of terms, so their sum is $(1 + 15)/2 \cdot 8 = 64$.

   Let the 5 consecutive even integers be $a$, $a + 2$, $a + 4$, $a + 6$, and $a + 8$. 
   Their sum is $5a + 20$.  But this is also $64 - 4 = 60$, so $5a + 20 = 60$.  Solving
   for $a$, we find $a = 8$.
*)

Require Import NArith.
Require Import List.
Import ListNotations.

Theorem mathd_algebra_158 a :
   list_sum (map (fun k => 2 * k + 1) (seq 0 8)) -
   list_sum (map (fun k => a + 2 * k) (seq 0 5)) = 4 ->
  a = 8.
Proof.
Admitted.
