(* miniF2F problem: mathd_algebra_480
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let \[f(x) = \begin{cases}
   -x^2 - 1 &\text{if }x<0, \\
   2&\text{if }0 \le x< 4, \\
   \sqrt{x}&\text{if }x \ge 4.
   \end{cases}
   \]Find $f(\pi)$. Show that it is 2.

   Informal proof:
   Since $\pi$ is about 3.14, we use the second case, so $f(\pi) = 2$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_480 (f : R -> R)
  (h0 : forall x : R, x < 0 -> f x = -(x^2) - 1)
  (h1 : forall x : R, 0 <= x -> x < 4 -> f x = 2)
  (h2 : forall x : R, x >= 4 -> f x = sqrt x) :
  f PI = 2.
Proof.
Admitted.
