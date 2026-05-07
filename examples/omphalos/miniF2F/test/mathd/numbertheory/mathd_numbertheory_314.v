(* miniF2F problem: mathd_numbertheory_314
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $r$ be the remainder when $1342$ is divided by $13$.

   Determine the smallest positive integer that has these two properties:

   $\bullet~$ It is a multiple of $1342$.

   $\bullet~$ Its remainder upon being divided by $13$ is smaller than $r$. Show that it
   is 6710.

   Informal proof:
   Note that \begin{align*}
   1342 &= 1300+39+3 \\
   &= 13(100+3)+3,
   \end{align*}so $r=3$.

   We are seeking the smallest multiple of $1342$ that is congruent to $0$, $1$, or $2$
   modulo $13$.

   We have $1342n \equiv 3n\pmod{13}$, so the remainders of the first four multiples of
   $1342$ are $3,6,9,12$. The next number in this sequence is $15$, but $15$ reduces to
   $2$ modulo $13$. That is: $$5\cdot 1342 \equiv 5\cdot 3 \equiv
   2\pmod{13}.$$Therefore, the number we are looking for is $5\cdot 1342 = 6710$.
*)

Require Import Nat.
Require Import Arith.

Theorem mathd_numbertheory_314 :
  forall (r n : nat),
  r = 1342 mod 13 ->
  0 < n ->
  Nat.divide 1342 n ->
  n mod 13 < r ->
  6710 <= n.
Proof.
Admitted.
