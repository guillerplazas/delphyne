(* miniF2F problem: mathd_algebra_215
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the sum of the two values of $x$ for which $(x+3)^2 = 121$? Show that it is
   -6.

   Informal proof:
   Expanding the left side, we have $x^2+6x+9=121 \Rightarrow x^2+6x-112=0$. For a
   quadratic with the equation $ax^2+bx+c=0$, the sum of the roots is $-b/a$. Applying
   this formula to the problem, we have that the sum of the two roots is $-6/1=-6$.
*)

Require Import Reals.
Require Import List.
Require Import Lra.

Open Scope R_scope.

Theorem mathd_algebra_215 (S : list R)
  (h₀ : forall x, In x S <-> (x + 3)^2 = 121) 
  (h₁ : NoDup S) :
  fold_right Rplus 0 S = -6.

Proof.
Admitted.
