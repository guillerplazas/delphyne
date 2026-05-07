(* miniF2F problem: mathd_algebra_441
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Assuming $x\ne0$, simplify $\frac{12}{x \cdot x} \cdot \frac{x^4}{14x}\cdot
   \frac{35}{3x}$. Show that it is 10.

   Informal proof:
   We have  \begin{align*}
   \frac{12}{x \cdot x} \cdot \frac{x^4}{14x}\cdot \frac{35}{3x} &=
   \frac{12 \cdot x^4 \cdot 35}{x^2\cdot 14x \cdot 3x}\\& = \frac{(4 \cdot 3) \cdot (5
   \cdot 7) \cdot x^4}{(3 \cdot 2 \cdot 7)(x^2 \cdot x \cdot x)}\\
   &= \frac{2\cdot 2 \cdot 3 \cdot 5 \cdot 7}{2 \cdot 3 \cdot 7}\cdot\frac{x^4}{x^{4}}\\
   &= 2 \cdot 5 = 10.
   \end{align*}
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_441 :
  forall x : R,
  x <> 0 ->
  12 / (x * x) * (x^4 / (14 * x)) * (35 / (3 * x)) = 10.
Proof.
Admitted.