(* miniF2F problem: mathd_numbertheory_483
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The Fibonacci sequence is the sequence 1, 1, 2, 3, 5, $\ldots$ where each term is the
   sum of the previous two terms. What is the remainder when the $100^{\mathrm{th}}$
   term of the sequence is divided by 4? Show that it is 3.

   Informal proof:
   If we look at the terms of the sequence mod 4, we see that they follow a pattern of
   period 6: \begin{align*}
   F_1 &\equiv 1\pmod{4}, \\
   F_2 &\equiv 1\pmod{4}, \\
   F_3 &\equiv 2\pmod{4}, \\
   F_4 &\equiv 3\pmod{4}, \\
   F_5 &\equiv 1\pmod{4}, \\
   F_6 &\equiv 0\pmod{4}, \\
   F_7 &\equiv 1\pmod{4}, \\
   F_8 &\equiv 1\pmod{4},~\ldots
   \end{align*} Then we see that the terms repeat.  Therefore, the $100^{\text{th}}$
   term is the same as the $4^{\text{th}}$ term, and thus has a remainder of $3$ when
   divided by 4.
*)

Require Import Nat.
Require Import ZArith.

Theorem mathd_numbertheory_483:
  forall a : nat -> nat,
  a 1 = 1 ->
  a 2 = 1 ->
  (forall n : nat, a (n + 2) = a (n + 1) + a n) ->
  a 100 mod 4 = 3.
Proof.
Admitted.