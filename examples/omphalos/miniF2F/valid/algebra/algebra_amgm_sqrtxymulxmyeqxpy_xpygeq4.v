(* miniF2F problem: algebra_amgm_sqrtxymulxmyeqxpy_xpygeq4
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose that $x$ and $y$ are positive real numbers with $y\leq x$, and that
   $\sqrt{xy}(x-y)=(x+y)$.
   Prove that $x+y\geq 4$.

   Informal proof:
   Since $x > y > 0$, it exists $\alpha \in (0, \pi/2)$ such that $y = x \cos \alpha$.
   So the equality $\sqrt{xy}(x-y)=(x+y)$ can be rewritten as
   \begin{eqnarray*}
   \frac{1}{\sqrt{xy}} = \frac{1-\frac{y}{x}}{1+\frac{y}{x}} = \frac{1 - \cos
   \alpha}{1+\cos \alpha} = \frac{1}{x \sqrt{\cos \alpha}}.
   \end{eqnarray*}
   So we have
   \[x = \frac{1+\cos\alpha}{\sqrt{\cos \alpha}(1 - \cos \alpha)}.\]
   Thus,
   \[x + y = x (1+\cos\alpha) = \frac{(1+\cos\alpha)^2}{\sqrt{\cos \alpha}(1 - \cos
   \alpha)}.\]
   Let $t = \sqrt{\cos\alpha}$ and consider the function
   \[f(t) = \frac{(1+t^2)^2}{t(1-t^2)}\]
   with $t \in (0,1)$. The derivative of $f$ is
   \[f'(t) = \frac{(1+t^2)(-t^4 + 6t^2 -1)}{t^2(1-t^2)^2}.\]
   Solving $f'(t) = 0$, we obtain
   \[t^2 = 3-2\sqrt{2} \quad \mbox{ or } \quad t^2 = 3+2\sqrt{2}.\]
   Since $t < 1$, we have
   \[t^2 = 3-2\sqrt{2} \quad \Longrightarrow \quad t = \sqrt{2} - 1.\]
   For $t^2 < 3 - 2\sqrt{2}$, i.e., $0 < t < \sqrt{2} - 1$, we have $f'(t) < 0$, so $f$
   is strictly decreasing in $(0, \sqrt{2} - 1)$; for $1 > t^2 > 3 - 2\sqrt{2}$, i.e.,
   $\sqrt{2} - 1 < t < 1$, we have $f'(t) > 0$, so $f$ is strictly increasing in
   $(\sqrt{2} - 1, 1)$.

   So, we have
   \[x + y = f(t) \geq \min_{0<t<1} f(t) = f(\sqrt{2} - 1) = 4.\]
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_amgm_sqrtxymulxmyeqxpy_xpygeq4 :
  forall x y : R,
  (0 < x /\ 0 < y) ->
  y <= x ->
  sqrt (x * y) * (x - y) = (x + y) ->
  x + y >= 4.
Proof.
Admitted.