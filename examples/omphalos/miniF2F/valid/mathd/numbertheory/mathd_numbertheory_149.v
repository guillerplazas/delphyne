(* miniF2F problem: mathd_numbertheory_149
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   A group of $N$ students, where $N < 50$, is on a field trip. If their teacher puts
   them in groups of 8, the last group has 5 students. If their teacher instead puts
   them in groups of 6, the last group has 3 students. What is the sum of all possible
   values of $N$? Show that it is 66.

   Informal proof:
   We are given that $N\equiv 5\pmod{8}$ and $N\equiv 3\pmod{6}$.  We begin checking
   numbers which are 5 more than a multiple of 8, and we find that 5 and 13 are not 3
   more than a multiple of 6, but 21 is 3 more than a multiple of 6. Thus 21 is one
   possible value of $N$. By the Chinese Remainder Theorem, the integers $x$ satisfying
   $x\equiv 5\pmod{8}$ and $x\equiv 3\pmod{6}$ are those of the form
   $x=21+\text{lcm}(6,8)k = 21 + 24 k$, where $k$ is an integer. Thus the 2 solutions
   less than $50$ are 21 and $21+24(1) = 45$, and their sum is $21+45=66$.
*)

Require Import List.
Require Import Nat.
Require Import PArith.
Require Import Bool.
Import ListNotations.

Theorem mathd_numbertheory_149:
  fold_left plus
    (filter (fun x => andb (Nat.eqb (x mod 8) 5) (Nat.eqb (x mod 6) 3))
           (seq 0 50))
    0 = 66.

Proof.
Admitted.
