(* miniF2F problem: mathd_algebra_137
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Because of redistricting, Liberty Middle School's enrollment increased to 598
   students. This is an increase of $4\%$ over last year's enrollment. What was last
   year's enrollment? Show that it is 575\text{ students}.

   Informal proof:
   If we knew last year's enrollment at Liberty Middle School, we would multiply by
   $1.04$ to get the new enrollment of $598$ students. Working backward, we can divide
   $598$ by $1.04$ to get $575\text{ students}$. Alternatively, we could solve the
   equation $x + 0.04x = 598$, where $x$ is last year's enrollment.
*)

Require Import Reals.
Require Import Nat.
Require Import Coq.Init.Nat.

Theorem mathd_algebra_137 :
  forall x : nat,
  (IZR (Z_of_nat x) + (4/100) * IZR (Z_of_nat x))%R = 598%R ->
  x = 575.
Proof.
Admitted.
