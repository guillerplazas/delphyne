(* miniF2F problem: mathd_algebra_15
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $a * b = a^b + b^a$, for all positive integer values of $a$ and $b$, then what is
   the value of $2 * 6$? Show that it is 100.

   Informal proof:
   We can see that $2 * 6 = 2^6 + 6^2 = 64 + 36 = 100$.
*)

Require Import Nat.
Require Import Arith.

Theorem mathd_algebra_15
  (s : nat -> nat -> nat)
  (h0 : forall a b, 0 < a -> 0 < b -> s a b = a ^ b + b ^ a) :
  s 2 6 = 100.
Proof.
Admitted.