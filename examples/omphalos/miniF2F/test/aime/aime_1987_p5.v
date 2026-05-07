(* miniF2F problem: aime_1987_p5
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find $3x^2 y^2$ if $x$ and $y$ are [[integer]]s such that $y^2 + 3x^2 y^2 = 30x^2 +
   517$. Show that it is 588.

   Informal proof:
   If we move the $x^2$ term to the left side, it is [[SFFT|factorable]]:

   $(3x^2 + 1)(y^2 - 10) = 517 - 10$

   $507$ is equal to $3 \cdot 13^2$. Since $x$ and $y$ are integers, $3x^2 + 1$ cannot
   equal a multiple of three. $169$ doesn't work either, so $3x^2 + 1 = 13$, and $x^2 =
   4$. This leaves $y^2 - 10 = 39$, so $y^2 = 49$. Thus, $3x^2 y^2 = 3 \times 4 \times
   49 = 588$.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem aime_1987_p5:
  forall (x y : Z), 
  (y ^ 2 + 3 * (x ^ 2 * y ^ 2) = 30 * x ^ 2 + 517) ->
  3 * (x ^ 2 * y ^ 2) = 588.
Proof.
Admitted.