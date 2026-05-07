(* miniF2F problem: mathd_algebra_101
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For what values of $x$ is it true that $x^2 - 5x - 4 \le 10$? Express your answer in
   interval notation. Show that it is x \in [-2,7].

   Informal proof:
   Re-arranging, $x^2 - 5x - 14 \le 0$. The left-hand quadratic factors as $x^2 - 5x -
   14 = (x - 7)(x + 2) \le 0$. Thus, $x-7$ and $x+2$ have opposite signs, so $-2 \le x
   \le 7$ and $x \in [-2,7]$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_101:
  forall x : R, (x^2 - 5 * x - 4 <= 10) -> (x >= -2) /\ (x <= 7).
Proof.
Admitted.