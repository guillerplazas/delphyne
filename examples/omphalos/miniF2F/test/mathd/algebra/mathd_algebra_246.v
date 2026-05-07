(* miniF2F problem: mathd_algebra_246
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $f(x)=ax^4-bx^2+x+5$ and $f(-3)=2,$ then what is the value of $f(3)$? Show that it
   is 8.

   Informal proof:
   Evaluating $f(x)$ for $x=3$ and $x=-3$, we have \[\left\{ \begin{aligned} f(3)& = a
   \cdot 3^4 - b \cdot 3^2 + 3 + 5, \\ f(-3) &= a \cdot (-3)^4 - b \cdot (-3)^2 + (-3) +
   5. \end{aligned} \right.\]If we subtract the second equation from the first equation,
   all the terms but one cancel out, and we get \[f(3) - f(-3) = 3 - (-3) = 6.\]Thus, if
   $f(-3) = 2,$ then $f(3) = f(-3) + 6 = 2 + 6 = 8.$
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_246
  (a b : R)
  (f : R -> R)
  (h₀ : forall x, f x = a * x^4 - b * x^2 + x + 5)
  (h₂ : f (-3) = 2) :
  f 3 = 8.
Proof.
Admitted.