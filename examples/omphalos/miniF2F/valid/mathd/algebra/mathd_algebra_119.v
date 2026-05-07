(* miniF2F problem: mathd_algebra_119
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Solve for $e$, given that $2d$ is $8$ less than $17e$, and $2e$ is $9$ less than $d$.
   Show that it is 2.

   Informal proof:
   We begin with a system of two equations \begin{align*}
   2d&=17e-8
   \\2e&=d-9
   \end{align*}Since the second equation can also be rewritten as $d=2e+9$, we can plug
   this expression for $d$ back into the first equation and solve for $e$ \begin{align*}
   2d&=17e-8
   \\\Rightarrow \qquad 2(2e+9)&=17e-8
   \\\Rightarrow \qquad 4e+18&=17e-8
   \\\Rightarrow \qquad -13e&=-26
   \\\Rightarrow \qquad e&=2.
   \end{align*}
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_119:
  forall (d e : R), 
  (2 * d = 17 * e - 8) -> 
  (2 * e = d - 9) -> 
  e = 2.
Proof.
Admitted.