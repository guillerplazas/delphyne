(* miniF2F problem: mathd_numbertheory_257
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Cards are numbered from 1 to 100. One card is removed and the values on the other 99
   are added. The resulting sum is a multiple of 77. What number was on the card that
   was removed? Show that it is 45.

   Informal proof:
   The sum of the numbers from 1 to 100 is \[1 + 2 + \dots + 100 = \frac{100 \cdot
   101}{2} = 5050.\] When this number is divided by 77, the remainder is 45.  Therefore,
   the number that was removed must be congruent to 45 modulo 77.

   However, among the numbers 1, 2, $\dots$, 100, only the number $45$ itself is
   congruent to 45 modulo 77.  Therefore, this was the number of the card that was
   removed.
*)

Require Import Nat.
Require Import List.
Import ListNotations.

Theorem mathd_numbertheory_257 :
  forall x : nat,
  (1 <= x /\ x <= 100) ->
  (exists k, k * 77 = fold_right plus 0 (seq 0 101) - x) ->
  x = 45.

Proof.
Admitted.
