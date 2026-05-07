(* miniF2F problem: mathd_algebra_176
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Expand the product $(x+1)^2 \cdot x$. Show that it is x^3 + 2x^2 + x.

   Informal proof:
   We have $(x+1)^2 = (x+1)(x+1) = x(x) + 1(x) + 1(x) + 1 = x^2 + 2x + 1$. Multiplying
   this by $x$ gives $x^3 + 2x^2 + x$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_176 (x : R) : (x + 1)^2 * x = x^3 + 2 * x^2 + x.
Proof.
Admitted.