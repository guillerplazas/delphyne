(* miniF2F problem: induction_ineq_nsqlefactn
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any integer $n \geq 4$, we have $n^2 \leq n!$.

   Informal proof:
   First, we observe that $n \leq (n-1)(n-2)$ as $n^2 - 4n + 2$ is positive for $n \geq
   4$.
   As a result, $(n-1)! \geq (n-1) (n-2) \geq n$. By multiplying by $n$ on each side, we
   get $n! \geq n^2$.
*)

Require Import Coq.Arith.Arith.
Require Import Coq.Arith.PeanoNat.
Require Import Coq.Init.Nat.
Require Import Coq.ZArith.BinInt.

Theorem induction_ineq_nsqlefactn :
  forall n : nat,
  4 <= n ->
  n^2 <= fact n.
Proof.
Admitted.