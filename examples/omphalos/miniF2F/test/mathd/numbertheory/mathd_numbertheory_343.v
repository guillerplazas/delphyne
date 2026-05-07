(* miniF2F problem: mathd_numbertheory_343
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the units digit of the product of all of the odd integers between 0 and 12?
   Show that it is 5.

   Informal proof:
   Let $N$ be the product of all odd integers between 0 and 12. Thus,
   $N=1\times3\times5\times7\times9\times11= 5(1\times3\times7\times9\times11)$. The
   product of odd integers is odd, and the units digit of 5 times any odd number is $5$.
   Therefore,  the units digit of $N$ is $5$.
*)

Require Import Nat.
Require Import List.
Require Import Arith.

Theorem mathd_numbertheory_343:
  (fold_left mult (map (fun k => 2 * k + 1) (seq 0 6)) 1) mod 10 = 5.
Proof.
Admitted.