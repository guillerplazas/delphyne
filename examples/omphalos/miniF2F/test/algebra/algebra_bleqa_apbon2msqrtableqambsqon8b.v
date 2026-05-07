(* miniF2F problem: algebra_bleqa_apbon2msqrtableqambsqon8b
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $a$ and $b$ be positive real numbers such that $b \leq a$. Show that
   $\frac{a+b}{2} - \sqrt{ab} \leq \frac{(a-b)^2}{8b}$.

   Informal proof:
   We have that $\frac{a+b}{2} - \sqrt{ab} = \frac{\left(\sqrt{a} -
   \sqrt{b}\right)^2}{2}$.
   But $\frac{\left(\sqrt{a} - \sqrt{b}\right)^2}{2} = \frac{(a-b)^2}{2 (\sqrt{a} +
   \sqrt{b})^2}$ so $\frac{a+b}{2} - \sqrt{ab} = \frac{(a-b)^2}{2 (\sqrt{a} +
   \sqrt{b})^2}$.
   Since $a \geq b$, $2(\sqrt{a} + \sqrt{b})^2 \geq 2 (2\sqrt{b})^2 = 8b$ and
   $\frac{(a-b)^2}{2 (\sqrt{a} + \sqrt{b})^2} \leq \frac{(a-b)^2}{8b}$.
   As a result, $\frac{a+b}{2} - \sqrt{ab} \leq \frac{(a-b)^2}{8b}$.
*)

Require Import Reals.

Open Scope R_scope.

Theorem algebra_bleqa_apbon2msqrtableqambsqon8b
  (a b : R)
  (h0 : 0 < a /\ 0 < b)
  (h1 : b <= a) :
  (a + b) / 2 - sqrt (a * b) <= ( (a - b) ^2 ) / (8 * b).
Proof.
Admitted.