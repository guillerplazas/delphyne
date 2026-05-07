(* miniF2F problem: mathd_algebra_51
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Together, Larry and Lenny have $\$$35. Larry has two-fifths of Lenny's amount. How
   many more dollars than Larry does Lenny have? Show that it is 15.

   Informal proof:
   Call the amount of money Larry has $a$ and the amount of money Lenny has $b$. We can
   use the following system of equations to represent the given information:
   \begin{align*}
   a + b &= 35 \\
   a &= \frac{2}{5} \cdot b \\
   \end{align*} Substituting for $a$ into the first equation gives $\frac{2}{5} b + b =
   35$. Solving for $b$ gives $\frac{7}{5} b = 35$, or $b = 25$. Thus, $a = 35 - 25 =
   10$. So Lenny has $25 - 10 = 15$ more dollars than Larry.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_51:
  forall a b : R,
  0 < a -> 0 < b ->
  a + b = 35 ->
  a = (2/5) * b ->
  b - a = 15.
Proof.
Admitted.