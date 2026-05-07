(* miniF2F problem: amc12_2000_p20
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $x,y,$ and $z$ are positive numbers satisfying

   $x + \frac{1}{y} = 4,\qquad y + \frac{1}{z} = 1, \qquad \text{and} \qquad z +
   \frac{1}{x} = \frac{7}{3}$

   Then what is the value of $xyz$ ?

   $\text {(A)}\ \frac{2}{3} \qquad \text {(B)}\ 1 \qquad \text {(C)}\ \frac{4}{3}
   \qquad \text {(D)}\ 2 \qquad \text {(E)}\ \frac{7}{3}$ Show that it is xyz = 1
   \rightarrow B.

   Informal proof:
   We multiply all given expressions to get:
   $(1)xyz + x + y + z + \frac{1}{x} + \frac{1}{y} + \frac{1}{z} + \frac{1}{xyz} =
   \frac{28}{3}$
   Adding all the given expressions gives that
   $(2) x + y + z + \frac{1}{x} + \frac{1}{y} + \frac{1}{z} = 4 + \frac{7}{3} + 1 =
   \frac{22}{3}$
   We subtract $(2)$ from $(1)$ to get that $xyz + \frac{1}{xyz} = 2$. Hence, by
   inspection, $xyz = 1 \rightarrow B$.
   $$
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12_2000_p20 :
  forall x y z : R,
    0 < x -> 0 < y -> 0 < z ->
    x + / y = 4 -> y + / z = 1 -> z + / x = 7 / 3 ->
    x * y * z = 1.
Proof.
Admitted.