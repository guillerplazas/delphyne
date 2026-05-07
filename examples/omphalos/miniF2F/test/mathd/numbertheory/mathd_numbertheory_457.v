(* miniF2F problem: mathd_numbertheory_457
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the least positive integer $n$ such that $80325$ divides $n!$? Show that it
   is 17.

   Informal proof:
   We find the prime factorization of $80325$, which is $3^3 \cdot 5^2 \cdot 7 \cdot
   17$. The largest prime in the factorization is $17$, so $n$ is at least 17. Since
   there are three factors of $3$, two factors of $5$, and one factor of $7$ in the
   prime factorization of $17!$, the minimum value of $n$ is $17$.
*)

Require Import Nat.
Require Import Arith.

Theorem mathd_numbertheory_457 :
  forall n : nat,
  0 < n -> 
  Nat.divide 80325 (fact n) ->
  17 <= n.

Proof.
Admitted.
