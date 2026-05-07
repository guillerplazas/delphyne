(* miniF2F problem: mathd_numbertheory_301
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $j$ is a positive integer and the expression $(7j+3)$ is multiplied by 3 and then
   divided by 7, what is the remainder? Show that it is 2.

   Informal proof:
   First we multiply $(7j+3)$ by 3 to get $21j+9$. Now we divide by 7 and get
   $$\frac{21j+9}{7}=3j+\frac{9}{7}=3j+1+\frac{2}{7}.$$ Since $j$ is an integer, we know
   that $3j+1$ is also an integer. We're left with the fraction $\frac{2}{7}$ when we
   divided by 7, which means the remainder is $2$.
*)

Require Import Arith.
Require Import ZArith.

Open Scope nat_scope.

Theorem mathd_numbertheory_301:
  forall j : nat,
  j > 0 ->
  (3 * (7 * j + 3)) mod 7 = 2.
Proof.
Admitted.