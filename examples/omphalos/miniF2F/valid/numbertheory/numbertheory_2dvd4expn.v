(* miniF2F problem: numbertheory_2dvd4expn
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any positive integer $n$, $2$ divides $4^n$.

   Informal proof:
   We have $4^n = (2^2)^n = 2^{2n}$. Since $n > 0$ we have that $2n > 0$, so $2$ divides
   $4^n$.
*)

Require Import Nat.
Require Import Arith.

Theorem numbertheory_2dvd4expn :
  forall n : nat,
  n <> 0 ->
  Nat.divide 2 (4^n).

Proof.
Admitted.
