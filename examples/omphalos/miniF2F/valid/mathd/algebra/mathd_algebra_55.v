(* miniF2F problem: mathd_algebra_55
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What fraction is the same as \[
   \frac{2-4+6-8+10-12+14}{3-6+9-12+15-18+21}?
   \] Show that it is \frac{2}{3}.

   Informal proof:
   We have \begin{align*}
   &\frac{2-4+6-8+10-12+14}{3-6+9-12+15-18+21} \\
   & \qquad = \frac{2(1-2+3-4+5-6+7)}{3(1-2+3-4+5-6+7)} \\
   & \qquad = \frac{2}{3}.
   \end{align*}
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_55:
  (2 - 4 + 6 - 8 + 10 - 12 + 14) / (3 - 6 + 9 - 12 + 15 - 18 + 21) = 2 / 3.
Proof.
Admitted.
