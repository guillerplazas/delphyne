(* miniF2F problem: mathd_numbertheory_12
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   How many integers between 15 and 85 are divisible by 20? Show that it is 4.

   Informal proof:
   For integers divisible by 20, we look for multiples of 20. The least and greatest
   multiples of 20 between 15 and 85 are 20 and 80, respectively. Between those two
   multiples of 20 are 40 and 60. So there are $4$ multiples of 20 between 15 and 85.
*)

Require Import Nat.
Require Import List.

Open Scope nat_scope.

Theorem mathd_numbertheory_12:
  length (filter (fun x => x mod 20 =? 0) (seq 15 (86-15))) = 4.
Proof.
Admitted.
