(* miniF2F problem: mathd_algebra_342
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The sum of the first 5 terms of an arithmetic series is $70$.  The sum of the first
   10 terms of this  arithmetic series is $210$.  What is the first term of the series?
   Show that it is \frac{42}{5}.

   Informal proof:
   Let the first term be $a$ and the common difference be $d$.  The sum of an arithmetic
   series is equal to the average of the first and last term, multiplied by the number
   of terms.  The fifth term is $a + 4d$, so the sum of the first five terms is
   \[\frac{a + (a + 4d)}{2} \cdot 5 = 5a + 10d = 70,\]which implies that $a + 2d = 14$,
   so $2d = 14 - a$.

   The tenth term is $a + 9d$, so the sum of the first ten terms is \[\frac{a + (a +
   9d)}{2} \cdot 10 = 10a + 45d = 210,\]which implies that $2a + 9d = 42$, so $9d = 42 -
   2a$.

   From the equation $2d = 14 - a$, $18d = 126 - 9a$, and from the equation $9d = 42 -
   2a$, $18d = 84 - 4a$, so \[126 - 9a = 84 - 4a.\]Then $5a = 42$, so $a =
   \frac{42}{5}$.
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.


Fixpoint sum_f_R0 (f : nat -> R) (n : nat) : R :=
  match n with
  | O => 0
  | S n' => sum_f_R0 f n' + f n'
  end.

Theorem mathd_algebra_342 :
  forall (a d : R),
    sum_f_R0 (fun k => a + INR k * d) 5 = 70 ->
    sum_f_R0 (fun k => a + INR k * d) 10 = 210 ->
    a = 42 / 5.

Proof.
Admitted.
