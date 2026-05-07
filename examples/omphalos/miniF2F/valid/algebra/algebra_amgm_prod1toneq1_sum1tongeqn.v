(* miniF2F problem: algebra_amgm_prod1toneq1_sum1tongeqn
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any real-valued function $a$ on the natural numbers such that $\forall
   i \in \mathbb{N}, a_i \geq 0$, if $prod_{i=0}^{n-1} a_i = 1$, then $sum_{i=0}^{n-1}
   a_i \geq n$.

   Informal proof:
   By AM-GM, we have
   $\frac{1}{n}\sum_{i=0}^{n-1}a(i)\geq\sqrt[n]{\prod_{i=0}^{n-1}a(i)}=1$. Multiplying
   by n gives the result.
*)


Require Import Reals.
Require Import List.
Import ListNotations.
Open Scope R_scope.


Definition Rsum (n : nat) (a : nat -> R) :=
  fold_right Rplus 0 (map a (seq 0 n)).

Definition Rprod (n : nat) (a : nat -> R) :=
  fold_right Rmult 1 (map a (seq 0 n)).


Theorem algebra_amgm_prod1toneq1_sum1tongeqn :
  forall (a : nat -> R) (n : nat),
    (forall i, 0 <= a i) ->
    Rprod n a = 1 ->
    Rsum n a >= INR n.

Proof.
Admitted.
