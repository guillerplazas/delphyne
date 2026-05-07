(* miniF2F problem: amc12_2000_p6
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Two different prime numbers between $4$ and $18$ are chosen. When their sum is
   subtracted from their product, which of the following numbers could be obtained?

   $\textbf{(A)}\ 22 \qquad\textbf{(B)}\ 60 \qquad\textbf{(C)}\ 119 \qquad\textbf{(D)}\
   180 \qquad\textbf{(E)}\ 231$ Show that it is \textbf{(C) }119.

   Informal proof:
   Any two prime numbers between 4 and 18 have an odd product and an even sum. Any odd
   number minus an even number is an odd number, so we can eliminate A, B, and D. Since
   the highest two prime numbers we can pick are 13 and 17, the highest number we can
   make is $(13)(17)-(13+17) = 221 - 30 = 191$. Thus, we can eliminate E. So, the answer
   must be $\textbf{(C) }119$.
*)

Require Import ZArith.
Require Import Nat.
Require Import PArith.
Require Import Arith.
Require Import Znumtheory.
Require Import Lia.

Theorem amc12_2000_p6 (p q : Z) :
    0 < p -> 0 < q ->
    prime p -> prime q ->
    (4 <= p <= 18)%Z ->
    (4 <= q <= 18)%Z ->
    p * q - (p + q) <> 194.
Proof.
Admitted.
