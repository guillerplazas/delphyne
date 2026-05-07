(* miniF2F problem: algebra_ineq_nto1onlt2m1on
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $n$ be a positive natural number. Show that $n^{1/n} \leq 2 - 1/n$.

   Informal proof:
   The result is trivially true for $n=1,2,3$.
   Let us define $f : x \longrightarrow x^{\frac{1}{x}}+x$. We have that $f$ is defined
   on $[3, \infty[$ and that $f'(x) = x^{\frac{1}{x}} \frac{1-\ln(x)}{x^2} -
   \frac{1}{x^2}$. For $x \geq 3$, we have that $1-\ln{x} < 0$ so $f'(x) < 0$. So $f$ is
   decreasing on $[3, \infty[$. But $f(3) \leq 2$. As a result, $\forall x \geq 3, f(x)
   \leq 2$. This is in particular true for all $n \geq 3$. $n^{1/n} \leq 2 - 1/n$ being
   satisfied for $n=1,2,3$, we have that $n^{1/n} \leq 2 - 1/n$ for any natural number
   $n$.
*)

Require Import Reals.
Require Import Arith.

Open Scope R_scope.

Theorem algebra_ineq_nto1onlt2m1on :
  forall n : nat,
  (n >= 1)%nat ->
  Rpower (INR n) (1 / INR n) <= 2 - 1 / INR n.

Proof.
Admitted.
