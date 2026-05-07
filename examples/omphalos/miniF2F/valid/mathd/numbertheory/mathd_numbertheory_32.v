(* miniF2F problem: mathd_numbertheory_32
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the sum of all of the positive factors of $36$? Show that it is 91.

   Informal proof:
   We find the factor pairs of 36, which are $1\cdot36, 2\cdot18, 3\cdot12, 4\cdot9,
   6\cdot6$. The sum of these factors is $1+36+2+18+3+12+4+9+6=91$.
*)

Require Import Coq.Init.Nat.
Require Import Coq.Lists.List.
Import ListNotations.


Definition divides (d n : nat) : bool :=
  Nat.eqb (n mod d) 0.


Definition divisors (n : nat) : list nat :=
  filter (fun d => divides d n) (seq 1 n).


Fixpoint sum_list (l : list nat) : nat :=
  match l with
  | [] => 0
  | x :: xs => x + sum_list xs
  end.


Theorem mathd_numbertheory_32 : sum_list (divisors 36) = 91.

Proof.
Admitted.
