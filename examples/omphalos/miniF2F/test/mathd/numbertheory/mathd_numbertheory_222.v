(* miniF2F problem: mathd_numbertheory_222
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The least common multiple of two numbers is 3720, and their greatest common divisor
   is 8. Given that one of the numbers is 120, what is the other number? Show that it is
   248.

   Informal proof:
   We know that $\gcd(a,b) \cdot \mathop{\text{lcm}}[a,b] = ab$ for all positive
   integers $a$ and $b$.  Hence, in this case, the other number is $8 \cdot 3720/120 =
   248$.
*)

Require Import Arith.

Theorem mathd_numbertheory_222:
  forall b : nat,
    Nat.lcm 120 b = 3720 ->
    Nat.gcd 120 b = 8 ->
    b = 248.
Proof.
Admitted.