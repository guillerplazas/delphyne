(* miniF2F problem: mathd_algebra_293
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Calculate $\sqrt{60x} \cdot \sqrt{12x} \cdot \sqrt{63x}$ . Express your answer in
   simplest radical form in terms of $x$.

   Note: When entering a square root with more than one character, you must use
   parentheses or brackets.  For example, you should enter $\sqrt{14}$ as ''sqrt(14)''
   or ''sqrt{14}''. Show that it is 36x \sqrt{35x}.

   Informal proof:
   Writing everything in terms of prime factorizations, the given expression is 
   \begin{align*}
   &\sqrt{3 \cdot 5 \cdot 2^2 \cdot 3 \cdot 2^2 \cdot 7 \cdot 3^2 \cdot x^3} \\
   & \qquad = \sqrt{(3^4 \cdot 2^4 \cdot x^2) \cdot (5 \cdot 7 \cdot x)} \\
   & \qquad = 36x \sqrt{35x}.
   \end{align*}
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_293 : forall x : R, 0 <= x ->
  sqrt (60 * x) * sqrt (12 * x) * sqrt (63 * x) = 36 * x * sqrt (35 * x).
Proof.
Admitted.