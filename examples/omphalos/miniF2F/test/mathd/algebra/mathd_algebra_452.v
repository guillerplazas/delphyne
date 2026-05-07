(* miniF2F problem: mathd_algebra_452
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The first and ninth terms of an arithmetic sequence are $\frac23$ and $\frac45$,
   respectively. What is the fifth term? Show that it is \frac{11}{15}.

   Informal proof:
   Since the fifth term is halfway between the first term and ninth term, it is simply
   the average of these terms, or \[\frac{2/3 + 4/5}{2} = \frac{11}{15}.\]
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_452 :
  forall (a : nat -> R),
  (forall n : nat, a (S (S n)) - a (S n) = a (S n) - a n) ->
  a (1%nat) = 2/3 ->
  a (9%nat) = 4/5 ->
  a (5%nat) = 11/15.

Proof.
Admitted.
