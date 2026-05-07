(* miniF2F problem: mathd_numbertheory_227
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   One morning each member of Angela's family drank an 8-ounce mixture of coffee with
   milk. The amounts of coffee and milk varied from cup to cup, but were never zero.
   Angela drank a quarter of the total amount of milk and a sixth of the total amount of
   coffee. How many people are in the family? Show that it is 5.

   Informal proof:
   Suppose that the whole family drank $x$ cups of milk and $y$ cups of coffee. Let $n$
   denote the number of people in the family. The information given implies that
   $\frac{x}{4}+\frac{y}{6}=\frac{x+y}{n}$. This leads to \[
   3x(n-4)=2y(6-n).
   \]Since $x$ and $y$ are positive, the only positive integer $n$ for which both sides
   have the same sign is $n=5$.
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.



Theorem mathd_numbertheory_227:
  forall (x y n : nat),
    x <> 0%nat ->
    y <> 0%nat ->
    n <> 0%nat ->
    (INR x / 4 + INR y / 6 = (INR x + INR y) / INR n) ->
    n = 5%nat.

Proof.
Admitted.
