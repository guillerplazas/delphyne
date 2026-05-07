(* miniF2F problem: mathd_numbertheory_296
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the smallest positive integer, other than $1$, that is both a perfect cube
   and a perfect fourth power? Show that it is 4096.

   Informal proof:
   If $n$ is a perfect cube, then all exponents in its prime factorization are divisible
   by $3$. If $n$ is a perfect fourth power, then all exponents in its prime
   factorization are divisible by $4$. The only way both of these statements can be true
   is for all the exponents to be divisible by $\mathop{\text{lcm}}[3,4]=12$, so such an
   $n$ must be a perfect twelfth power. Since we aren't using $1^{12}=1,$ the next
   smallest is $2^{12}=4096.$
*)

Require Import Coq.Arith.Arith.
Require Import Coq.ZArith.ZArith.
Open Scope nat_scope.

Theorem mathd_numbertheory_296:
  forall n : nat,
  2 <= n ->
  exists x, x^3 = n ->
  exists t, t^4 = n ->
  4096 <= n.
Proof.
Admitted.