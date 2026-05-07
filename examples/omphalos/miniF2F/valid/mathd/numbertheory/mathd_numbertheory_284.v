(* miniF2F problem: mathd_numbertheory_284
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What positive two-digit integer is exactly twice the sum of its digits? Show that it
   is 18.

   Informal proof:
   Let the tens digit of the two-digit integer be $a$ and let its units digit be $b$. 
   The equation \[
   10a+b=2(a+b)
   \] is given.  Distributing on the right-hand side and subtracting $2a+b$ from both
   sides gives $8a=b$.  Since $8a>9$ for any digit $a>1$, we have $a=1$, $b=8$, and
   $10a+b=18$.
*)

Require Import Nat.
Require Import ZArith.

Theorem mathd_numbertheory_284 :
  forall a b : nat,
  1 <= a /\ a <= 9 /\ b <= 9 ->
  10 * a + b = 2 * (a + b) ->
  10 * a + b = 18.
Proof.
Admitted.