(* miniF2F problem: imo_1964_p1_1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $n$ be a natural number. Show that if $7$ divides $2^n-1$, then $3$ divides $n$.

   Informal proof:
   Since we know that $2^n-1$ is congruent to 0 (mod 7), we know that $2^n$ is congruent
   to 8 mod 7, which means $2^n$ is congruent to 1 mod 7.

   Experimenting with the residue of $2^n$ mod 7: 

   $n$=1: 2
   $n$=2: 4
   $n$=3: 1 (this is because when $2^n$ is doubled to $2*2^n$, the residue doubles too,
   but $4*2=8$ is congruent to 1 (mod 7).

   $n$=4: 2
   $n$=5: 4
   $n$=6: 1

   Through induction, we easy show that this is true since the residue doubles every
   time you double $2^n$.

   So, the residue of $2^n$ mod 7 cycles in 2, 4, 1. Therefore, $n$ must be a multiple
   of 3.
*)

Require Import Arith.

Theorem imo_1964_p1_1 :
  forall n : nat,
  (Nat.divide 7 (2^n - 1)) -> (Nat.divide 3 n).

Proof.
Admitted.
