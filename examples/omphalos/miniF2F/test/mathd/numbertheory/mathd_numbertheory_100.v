(* miniF2F problem: mathd_numbertheory_100
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find $n$ if $\gcd(n,40) = 10$ and $\mathop{\text{lcm}}[n,40] = 280$. Show that it is
   70.

   Informal proof:
   We know that $\gcd(a,b) \cdot \mathop{\text{lcm}}[a,b] = ab$ for all positive
   integers $a$ and $b$.  Hence, in this case, $10 \cdot 280 = n \cdot 40$, so $n = 10
   \cdot 280/40 = 70$.
*)

Require Import Coq.Arith.PeanoNat.
Require Import Coq.Init.Nat.
Require Import Coq.ZArith.Znat.
Open Scope nat_scope.

Theorem mathd_numbertheory_100:
  forall n : nat,
  0 < n ->
  Nat.gcd n 40 = 10 ->
  Nat.lcm n 40 = 280 ->
  n = 70.
Proof.
Admitted.