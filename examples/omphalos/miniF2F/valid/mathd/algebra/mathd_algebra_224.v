(* miniF2F problem: mathd_algebra_224
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The square root of $t$ is greater than $2$ and less than $3.5$. How many integer
   values of $t$ satisfy this condition? Show that it is 8.

   Informal proof:
   We have: $2 < \sqrt{t} < \frac{7}{2}$ so squaring the inequality (which we can do
   because all the terms in it are positive) gives us  $4 < t <\frac{49}{4}=12.25$. 
   Therefore, $t$ is an integer between 5 and 12 inclusive, which leaves us with $8$
   possible integer values of $t$.
*)

Require Import Reals.
Require Import Finite_sets.
Require Import Finite_sets_facts.
Require Import Ensembles.

Open Scope R_scope.

Definition satisfies_condition (n : nat) : Prop :=
  (2 < sqrt (INR n))%R /\ (sqrt (INR n) < 7/2)%R.

Theorem mathd_algebra_224:
  cardinal nat (fun n => satisfies_condition n) 8.

Proof.
Admitted.
