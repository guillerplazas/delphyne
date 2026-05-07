(* miniF2F problem: mathd_numbertheory_711
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The greatest common divisor of positive integers $m$ and $n$ is 8. The least common
   multiple of $m$ and $n$ is 112. What is the least possible value of $m+n$? Show that
   it is 72.

   Informal proof:
   Since the GCD of $m$ and $n$ is 8, $m = 8x$ and $n = 8y$ for some integers $x$ and
   $y$.  Note that minimizing $m + n = 8x + 8y = 8(x + y)$ is equivalent to minimizing
   $x + y$.

   The LCM of $m$ and $n$ is $112 = 2^4 \cdot 7 = 8 \cdot 2 \cdot 7$, so one of $x$ and
   $y$ is divisible by 2 and one is divisible by 7.  Then we can minimize $x + y$ by
   setting $x$ and $y$ to be 2 and 7 in some order.  Therefore, the least possible value
   of $m+n$ is $8(2 + 7) = 72$.
*)

Require Import Nat.
Require Import PeanoNat.
Require Import Arith.

Theorem mathd_numbertheory_711:
  forall m n : nat,
  0 < m /\ 0 < n ->
  Nat.gcd m n = 8 ->
  Nat.lcm m n = 112 ->
  72 <= m + n.
Proof.
Admitted.