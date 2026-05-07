(* miniF2F problem: amc12a_2002_p13
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Two different positive numbers $a$ and $b$ each differ from their reciprocals by $1$.
   What is $a+b$?

   $
   \text{(A) }1
   \qquad
   \text{(B) }2
   \qquad
   \text{(C) }\sqrt 5
   \qquad
   \text{(D) }\sqrt 6
   \qquad
   \text{(E) }3
   $ Show that it is (C) \sqrt 5.

   Informal proof:
   Each of the numbers $a$ and $b$ is a solution to $\left| x - \frac 1x \right| = 1$.

   Hence it is either a solution to $x - \frac 1x = 1$, or to $\frac 1x - x = 1$. Then
   it must be a solution either to $x^2 - x - 1 = 0$, or to $x^2 + x - 1 = 0$.

   There are in total four such values of $x$, namely $\frac{\pm 1 \pm \sqrt 5}2$. 

   Out of these, two are positive: $\frac{-1+\sqrt 5}2$ and $\frac{1+\sqrt 5}2$. We can
   easily check that both of them indeed have the required property, and their sum is
   $\frac{-1+\sqrt 5}2 + \frac{1+\sqrt 5}2 = (C) \sqrt 5$.
*)

Require Import Reals.
Require Import Psatz.

Open Scope R_scope.

Theorem amc12a_2002_p13 :
  forall a b : R,
    0 < a -> 0 < b ->
    a <> b ->
    Rabs (a - 1/a) = 1 ->
    Rabs (b - 1/b) = 1 ->
    a + b = sqrt 5.
Proof.
Admitted.