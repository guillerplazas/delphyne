(* miniF2F problem: numbertheory_aneqprodakp4_anmsqrtanp1eq2
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $a_0 = 1$. For any positive integer $n$, let $a_{n+1} = \prod_{k = 1}^n a_k + 4$.
   Show that for any positive integer $n$, $a_n - \sqrt{a_{n+1}} = 2$.

   Informal proof:
   For $n\geq 1$, we have $a_{n+1} = \prod_{k=1}^n a_k + 4 = (\prod_{k=1}^{n-1} a_k
   ).a_n + 4 = (a_n - 4).a_n + 4 = a_n^2 - 4.a_n + 4 = (a_n - 2)^2.$
   Then $a_n - \sqrt{a_{n+1}} = a_n - \sqrt{(a_n - 2)^2}=2$
*)

Require Import Reals.
Require Import List.
Require Import Lia.

From Coquelicot Require Import Coquelicot.

Theorem numbertheory_aneqprodakp4_anmsqrtanp1eq2:
  forall (a : nat -> R),
  (a 0%nat = 1%R) ->
  (forall n : nat, a (S n) = (prod_f_R0 a n) + 4%R) ->
  forall n : nat,
  (n >= 1)%nat ->
  a n - sqrt (a (S n)) = 2%R.

Proof.
Admitted.
