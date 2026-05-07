(* miniF2F problem: mathd_algebra_440
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Jasmine drank 1.5 pints of water on the first 3 miles of her hike. If she continued
   at this rate, how many pints of water would she drink in the next 10 miles? Show that
   it is 5.

   Informal proof:
   We can set up the ratios $\frac{1.5}{3}=\frac{x}{10}$, where $x$ is how many pints of
   water she'd drink in the next 10 miles. We cross-multiply to get $3x=1.5(10)=15$,
   which means $x=5$. Jasmine would drink $5$ pints of water in the next 10 miles.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_440:
  forall x : R, (1.5 / 3 = x / 10) -> x = 5.
Proof.
Admitted.
