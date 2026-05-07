(* miniF2F problem: mathd_numbertheory_169
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the greatest common factor of $20 !$ and $200,\!000$?  (Reminder: If $n$ is a
   positive integer, then $n!$ stands for the product $1\cdot 2\cdot 3\cdot \cdots \cdot
   (n-1)\cdot n$.) Show that it is 40,\!000.

   Informal proof:
   The prime factorization of $200,000$ is $2^6 \cdot 5^5$. Then count the number of
   factors of $2$ and $5$ in $20!$. Since there are $10$ even numbers, there are more
   than $6$ factors of $2$. There are $4$ factors of $5$. So the greatest common factor
   is $2^6 \cdot 5^4=40,\!000$.
*)

Require Import Arith.

Theorem mathd_numbertheory_169 :
  Nat.gcd (fact 20) 200000 = 40000.
Proof.
Admitted.