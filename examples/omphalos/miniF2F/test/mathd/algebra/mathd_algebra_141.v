(* miniF2F problem: mathd_algebra_141
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   A rectangular patio has an area of $180$ square feet and a perimeter of $54$ feet.
   What is the length of the diagonal (in feet) squared? Show that it is 369.

   Informal proof:
   Set one side of the patio equal to $a$ and the other equal to $b$, producing two
   equations: \begin{align*}
   ab&=180,\text{ and}\\
   2a+2b&=54.
   \end{align*}The second equation can be rewritten as $b=27-a$. Substituting, we have
   \begin{align*}
   180&=a\left(27-a\right) \quad \Rightarrow \\
   180&=27a-a^2 \quad \Rightarrow \\
   -180&=a^2-27a \quad \Rightarrow \\
   0&=a^2-27a+180 \quad \Rightarrow \\
   0&=\left(a-12\right)\left(a-15\right).
   \end{align*}So $12$ feet and $15$ feet are the lengths of the two sides of the patio.
   Therefore, the diagonal is $\sqrt{12^2+15^2}$, or $\sqrt{369}$. Therefore, the length
   of the diagonal squared is $369$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_141
  (a b : R)
  (h₁ : a * b = 180)
  (h₂ : 2 * (a + b) = 54) :
  a^2 + b^2 = 369.
Proof.
Admitted.