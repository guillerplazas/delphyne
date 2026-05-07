(* miniF2F problem: mathd_algebra_400
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Five plus $500\%$ of $10$ is the same as $110\%$ of what number? Show that it is 50.

   Informal proof:
   We have $5+\frac{500}{100}\cdot10=5+5\cdot10=55$ equal to $110\%$ of the number $x$.
   $$\frac{110}{100}x=\frac{11}{10}x=55\qquad\Rightarrow
   x=55\cdot\frac{10}{11}=5\cdot10=50$$ The number is $50$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_400:
  forall x : R,
  (5 + 500 / 100 * 10 = 110 / 100 * x) ->
  x = 50.
Proof.
Admitted.