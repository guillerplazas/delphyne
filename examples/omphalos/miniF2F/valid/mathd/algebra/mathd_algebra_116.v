(* miniF2F problem: mathd_algebra_116
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For what real value of $k$ is $\frac{13-\sqrt{131}}{4}$ a root of $2x^2-13x+k$? Show
   that it is $\frac{19}{4}$.

   Informal proof:
   We could substitute $(13-\sqrt{131})/4$ for $x$ in the equation, but the quadratic
   formula suggests a quicker approach. Substituting $2$, $-13$, and $k$ into the
   quadratic formula gives  \[
   \frac{-(-13)\pm\sqrt{(-13)^2-4(2)(k)}}{2(2)}= \frac{13\pm\sqrt{169-8k}}{4}.
   \]Setting $(13+\sqrt{169-8k})/4$ and $(13-\sqrt{169-8k})/4$ equal to
   $(13-\sqrt{131})/4$, we find no solution in the first case and $169-8k=131$ in the
   second case.  Solving yields $k=(169-131)/8=38/8=\frac{19}{4}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_116 :
  forall (k x : R),
  x = (13 - sqrt 131) / 4 ->
  2 * x^2 - 13 * x + k = 0 ->
  k = 19/4.
Proof.
Admitted.