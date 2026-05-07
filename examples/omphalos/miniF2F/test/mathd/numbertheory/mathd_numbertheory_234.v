(* miniF2F problem: mathd_numbertheory_234
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   When the two-digit integer $``\text{AB}''$ is cubed, the value is $912,\!673$. What
   is $A + B$? Show that it is 16.

   Informal proof:
   Since $90^3=729,\!000$, $\text{AB}$ is greater than 90.  Therefore, $\text{A}=9$. 
   Since the ones digit of $\text{AB}^3$ is 3, $\text{AB}$ must be odd.  The ones digit
   of $\text{AB}^3$ is the same as the ones digit of $\text{B}^3$, so we look at the
   ones digits of the cubes of the odd digits. \[
   \begin{array}{c}
   \text{The ones digit of }1^3 \text{ is } 1. \\ \text{The ones digit of }3^3 \text{ is
   } 7. \\ \text{The ones digit of }5^3 \text{ is } 5. \\ \text{The ones digit of }7^3
   \text{ is } 3. \\ \text{The ones digit of }9^3 \text{ is } 9.
   \end{array}
   \] Only $7^3$ has a ones digit of 3, so $\text{B}=7$.  Therefore,
   $\text{A}+\text{B}=9+7=16$.
*)

Require Import Coq.Arith.PeanoNat.
Require Import Coq.Arith.Arith.

Theorem mathd_numbertheory_234 :
  forall a b : nat, 
  (1 <= a /\ a <= 9 /\ b <= 9) ->
  (10 * a + b)^3 = 912673 ->
  a + b = 16.
Proof.
Admitted.