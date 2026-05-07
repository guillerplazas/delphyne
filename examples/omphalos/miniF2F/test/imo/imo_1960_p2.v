(* miniF2F problem: imo_1960_p2
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For what values of the variable $x$ does the following inequality hold:

   $\dfrac{4x^2}{(1 - \sqrt {2x + 1})^2} < 2x + 9 \ ?$

   Informal proof:
   Set $x = -\frac{1}{2} + \frac{a^2}{2}$, where $a\ge0$.
   $\frac{4\left(-\frac{1}{2}+\frac{a^2}{2}\right)^2}{\left(1-\sqrt{1+2\left(-\frac{1}{2}+\frac{a^2}{2}\right)}\right)^2}<2\left(-\frac{1}{2}+\frac{a^2}{2}\right)+9$

   After simplifying, we get
   $(a+1)^2<a^2+8$

   So
   $a^2+2a+1<a^2+8$

   Which gives $a<\frac{7}{2}$ and hence $-\frac{1}{2} \le x<\frac{45}{8}$.

   But $x=0$ makes the LHS indeterminate.

   So, answer: $-\frac{1}{2} \le x<\frac{45}{8}$, except $x=0$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem imo_1960_p2 :
  forall (x : R),
  (0 <= 1 + 2 * x) ->
  (1 - sqrt (1 + 2 * x))^2 <> 0 ->
  (4 * x^2) / (1 - sqrt (1 + 2 * x))^2 < 2 * x + 9 ->
  - (1 / 2) <= x /\ x < 45 / 8.
Proof.
Admitted.