(* miniF2F problem: induction_sum2kp1npqsqm1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for positive integer n, $\sum_{k=0}^{n-1} (2k + 3) = (n + 1)^2 - 1$.

   Informal proof:
   We use induction. The base case for $n=1$ states 2*0+3 = 2^2-1 which is true.
   Assuming the result holds for $n\geq 0$, write $\sum_{k=0}^n (2k + 3) =
   \sum_{k=0}^{n-1} (2k + 3) + 2*n+3 = (n+1)^2 - 1 + 2n + 3 = n^2 + 4n + 4 - 1 = (n+2)^2
   -1$. This shows the result holds for $n+1$ and concludes the proof by induction.
*)

(* Step 1: Import necessary libraries.
   We need to perform finite summations over natural numbers.
   Coq's standard library provides the `List` module which can be used for summations.
   Alternatively, the `mathcomp` library offers more advanced features for finite sums.
   For simplicity, we'll use the `List` module here. *)

Require Import List.
Import ListNotations.
Require Import Arith.

(* Step 2: Define a function to compute the finite sum
   of a function over a range of natural numbers.
   We'll define `sum_f` which takes a function `f` and an upper bound `n`,
   and computes the sum of `f k` for `k` from `0` to `n - 1`. *)

Fixpoint sum_f (f : nat -> nat) (n : nat) : nat :=
  match n with
  | 0 => 0
  | S m => f m + sum_f f m
  end.

(* Step 3: State the theorem.
   The theorem `induction_sum2kp1npqsqm1` states that for any positive integer `n`,
   the sum of `2k + 3` for `k` from `0` to `n - 1` is equal to `(n + 1)^2 - 1`. *)

Theorem induction_sum2kp1npqsqm1 : forall n : nat,
  sum_f (fun k => 2 * k + 3) n = (n + 1) * (n + 1) - 1.
Proof.
Admitted.
