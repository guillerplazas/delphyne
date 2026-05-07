(* miniF2F problem: numbertheory_sumkmulnckeqnmul2pownm1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for positive integers $n$ and $k$, if $k \leq n$, then $\sum_{k=1}^n
   (k*C_n^k) = n * 2^{n-1}$.

   Informal proof:
   $\sum_{k=1}^n k \binom{n}{k} = \sum_{k=1}^n \frac{n(n-1)!}{(k-1)!(n-1 -(k-1))!} =
   n\sum_{k=1}^n \binom{n-1}{k-1} = n\sum_{k=0}^{n-1} \binom{n-1}{k} = n2^{n-1}$
*)

Require Import Nat.
Require Import BinNat.
Require Import Arith.
Require Import Coq.Init.Nat.

Fixpoint sum_n_m (f: nat -> nat) (n m: nat) : nat :=
  match m with
  | O => f n
  | S m' => f (n + m) + sum_n_m f n m'
  end.


Fixpoint binom (n k : nat) : nat :=
  match k with
  | 0 => 1
  | S k' => match n with
           | 0 => 0
           | S n' => (binom n' k' * S n' / S k')%nat
           end
  end.

Theorem numbertheory_sumkmulnckeqnmul2pownm1 :
  forall n : nat,
  0 < n ->
  sum_n_m (fun k => k * binom n k) 1 n = n * pow 2 (n - 1).

Proof.
Admitted.
