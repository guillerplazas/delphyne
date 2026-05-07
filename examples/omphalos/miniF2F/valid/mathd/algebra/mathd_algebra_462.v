(* miniF2F problem: mathd_algebra_462
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Evaluate: $\left( \frac{1}{2} + \frac{1}{3} \right) \left( \frac{1}{2} - \frac{1}{3}
   \right)$ Show that it is \frac{5}{36}.

   Informal proof:
   For any $x$ and $y$, $(x+y)(x-y)=x^2-y^2+xy-xy=x^2-y^2$, so \begin{align*}
   \left( \frac{1}{2} + \frac{1}{3} \right) \left( \frac{1}{2} - \frac{1}{3}
   \right)&=\left(\frac12\right)^2-\left(\frac13\right)^2\\
   &=\frac14-\frac19\\
   &=\frac{9}{36}-\frac{4}{36}\\
   &=\frac{5}{36}
   \end{align*}
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_462 :
  (1/2 + 1/3) * (1/2 - 1/3) = 5/36.
Proof.
Admitted.