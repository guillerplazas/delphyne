(* miniF2F problem: mathd_algebra_289
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The two positive integer solutions of the equation $x^2 - mx + n = 0$ are $k$ and
   $t$, where $m$ and $n$ are both prime numbers and $k > t$. What is the value of $m^n
   + n^m + k^t + t^k$? Show that it is 20.

   Informal proof:
   From $x^2-mx+n=0$, we get $k+t=m$ and $kt=n$. Since $n$ is prime, one of $k$ and $t$
   is $n$ and the other is 1. $k>t$, so $k=n$ and $t=1$. Then $m=n+1$. $m$ is also
   prime, so we have two consecutive integers that are prime. Since one of every two
   consecutive integers is even, and the only even prime is 2, we must have $n=2$ and
   $m=3$. Therefore, $m^n+n^m+k^t+t^k= 3^2+2^3+2^1+1^2=9+8+2+1=20$.
*)

Require Import ZArith.
Require Import Nat.

Definition is_prime (p: nat) := 
  p > 1 /\ forall m : nat, m > 0 /\ m < p -> p mod m <> 0 \/ m = 1.

Theorem mathd_algebra_289:
  forall (k t m n : nat),
    is_prime m -> is_prime n ->
    t < k ->
    (Z.of_nat (k * k) - Z.of_nat (m * k) + Z.of_nat n)%Z = 0%Z ->
    (Z.of_nat (t * t) - Z.of_nat (m * t) + Z.of_nat n)%Z = 0%Z ->
    m ^ n + n ^ m + k ^ t + t ^ k = 20.

Proof.
Admitted.
