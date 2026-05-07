(* miniF2F problem: mathd_numbertheory_299
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the ones digit of $1 \cdot 3 \cdot 5 \cdot 7 \cdot 9 \cdot 11 \cdot 13$? Show
   that it is 5.

   Informal proof:
   Instead of just starting to multiply, let's look around to see if we can make things
   easier first. We see that one of the numbers being multiplied is 5. The commutative
   and associative properties of multiplication allow us to write the product as \[
   1 \cdot 3 \cdot 5 \cdot 7 \cdot 9 \cdot 11 \cdot 13 = (\text{some big odd
   number})\cdot 5. \\
   \]Since $a\cdot 5$ has a ones digit of $5$ for any odd integer value of $a$, it
   doesn't matter what the big number is. The ones digit of the product is $5$.
*)

Require Import ZArith.

Open Scope Z_scope.

Theorem mathd_numbertheory_299 :
  (1 * 3 * 5 * 7 * 9 * 11 * 13) mod 10 = 5.
Proof.
Admitted.