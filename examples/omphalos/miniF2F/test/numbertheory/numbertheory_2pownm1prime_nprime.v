(* miniF2F problem: numbertheory_2pownm1prime_nprime
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that if $n$ is a positive integer and $2^n - 1$ is prime, then $n$ is prime.

   Informal proof:
   Let's assume that $n$ is not prime, and that there exists two integers $p$ and $q$
   such that $p \geq 2, q \geq 2$ and $n = pq$. We have:
   $$2^n - 1 = 2^{pq} - 1 = (2^p)^q - 1 = (2^p - 1) \times \left((2^p)^{q-1} + \dots +
   2^p + 1\right)$$
   So, $2^p - 1$ is a divisor of $2^n - 1$. Since $2^p - 1 \geq 2$, this contradicts the
   initial assumption which is that $n$ is not prime. Hence, $n$ is a prime number.
*)

Require Import ZArith.
Require Import Znumtheory.
Require Import PArith.

Open Scope Z_scope.

Theorem numbertheory_2pownm1prime_nprime:
  forall n : Z,
    n > 0 ->
    prime (2^n - 1) ->
    prime n.

Proof.
Admitted.
