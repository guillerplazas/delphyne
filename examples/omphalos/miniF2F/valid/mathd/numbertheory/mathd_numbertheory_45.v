(* miniF2F problem: mathd_numbertheory_45
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the result when the greatest common factor of 6432 and 132 is increased by
   11? Show that it is 23.

   Informal proof:
   We first recognize that $132=11\times 12$, so its prime factorization is $132 = 2^2
   \cdot 3 \cdot 11$. We only need to see if these three prime factors will divide into
   $6432$. Indeed, $6432$ will satisfy the divisibility properties for both $3$ and $4$,
   and we can long divide to see that $11$ does not divide into $6432$. Thus, the
   greatest common factor is $3 \times 4 = 12$. The greatest common factor increased by
   11 is $12+11 = 23$.
*)

Require Import ZArith.

Open Scope Z_scope.

Theorem mathd_numbertheory_45 :
  (Z.gcd 6432 132) + 11 = 23.
Proof.
Admitted.