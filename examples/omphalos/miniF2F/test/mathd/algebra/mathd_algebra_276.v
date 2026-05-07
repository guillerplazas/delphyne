(* miniF2F problem: mathd_algebra_276
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The expression $10x^2-x-24$ can be written as $(Ax-8)(Bx+3),$ where $A$ and $B$ are
   integers. What is $AB + B$? Show that it is 12.

   Informal proof:
   We see that $10x^2-x-24=(5x-8)(2x+3)$, thus $A = 5$ and $B = 2$. Hence, $AB + B =
   12.$
*)

Require Import Reals.
Require Import ZArith.

Open Scope R_scope.

Theorem mathd_algebra_276 :
  forall (a b : Z),
  (forall x : R, 10 * x^2 - x - 24 = (IZR a * x - 8) * (IZR b * x + 3)) ->
  Z.add (Z.mul a b) b = 12%Z.

Proof.
Admitted.
