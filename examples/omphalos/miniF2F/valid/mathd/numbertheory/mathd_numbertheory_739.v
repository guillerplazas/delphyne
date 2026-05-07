(* miniF2F problem: mathd_numbertheory_739
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For each positive integer $n$, let $n!$ denote the product $1\cdot 2\cdot
   3\cdot\,\cdots\,\cdot (n-1)\cdot n$.

   What is the remainder when $9!$ is divided by $10$? Show that it is 0.

   Informal proof:
   Notice that $10=2\cdot 5$. Both are factors of $9!$, so the remainder is $0$.
*)

Require Import Arith.
Require Import Nat.

Theorem mathd_numbertheory_739:
  (fact 9) mod 10 = 0.
Proof.
Admitted.