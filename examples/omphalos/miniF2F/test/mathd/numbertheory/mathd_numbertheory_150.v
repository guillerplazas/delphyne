(* miniF2F problem: mathd_numbertheory_150
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the smallest positive integer $N$ such that the value $7 + (30 \times N)$ is
   not a prime number? Show that it is 6.

   Informal proof:
   Since 2, 3, and 5 divide $30N$ but not $7$, they do not divide $30N + 7$.  Similarly,
   7 only divides $30N + 7$ if 7 divides $30N$, which means $N$ must be a multiple of 7
   for 7 to divide it.  Since no number less than 11 divides $30N + 7$ while $N < 7$, we
   only need to check when $30N + 7 \ge 11^2$.  When $N = 4$, $30N + 7 = 127$ is prime. 
   When $N = 5$, $30N + 7 = 157$ is prime.  However, when $N = 6$, $30N + 7 = 187 = 11
   \cdot 17$ is composite.
*)

Require Import Nat.
Require Import PeanoNat.
Require Import Arith.
Require Import ZArith.
Require Import Znumtheory.

Open Scope Z_scope.

Theorem mathd_numbertheory_150 :
  forall n : nat,
  ~ prime (Z.of_nat (7 + 30 * n)) -> Z.of_nat 6 <= Z.of_nat n.

Proof.
Admitted.
